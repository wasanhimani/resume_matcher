"""
Parsing layer: extracts raw text from resume files (PDF/DOCX), then pulls
out structured information — name, email, phone, skills, education,
years of experience — using a mix of regex and spaCy NLP.

This is intentionally kept rule-based/keyword-based rather than a black-box
model, so you can explain exactly how each piece works in your viva.
"""
import re
import os
import pdfplumber
import docx
import spacy

from src.skills_db import SKILLS_DB

# Load spaCy's English model once, reused across all parsing calls.
nlp = spacy.load("en_core_web_sm")

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\d{10}")
EXPERIENCE_YEARS_REGEX = re.compile(r"(\d+)\+?\s*(?:years|yrs)", re.IGNORECASE)

EDUCATION_KEYWORDS = [
    "B.Tech", "B.E.", "Bachelor", "M.Tech", "M.E.", "Master", "MBA",
    "PhD", "B.Sc", "M.Sc", "BCA", "MCA", "Diploma",
]


# ---------------- TEXT EXTRACTION ----------------

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file, page by page."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """Extracts all paragraph text from a DOCX file."""
    document = docx.Document(file_path)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_text(file_path: str) -> str:
    """Dispatches to the right extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ---------------- FIELD EXTRACTION ----------------

def extract_email(text: str) -> str | None:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_REGEX.search(text)
    return match.group(0) if match else None


def extract_name(text: str) -> str | None:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    of the resume, and/or the first PERSON entity spaCy finds near the top.
    We combine both for robustness.
    """
    first_line = next((line.strip() for line in text.split("\n") if line.strip()), None)

    # Run NER on just the first few lines (name is always near the top,
    # and this avoids false positives from names mentioned later, e.g. references).
    top_chunk = "\n".join(text.split("\n")[:5])
    doc = nlp(top_chunk)
    person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    if person_entities:
        # spaCy occasionally merges an adjacent line (e.g. email) into the
        # entity span when they sit close together in the layout. Clip at
        # the first newline and sanity-check it still looks like a name.
        candidate = person_entities[0].split("\n")[0].strip()
        looks_like_name = candidate and "@" not in candidate and not any(ch.isdigit() for ch in candidate)
        if looks_like_name:
            return candidate

    return first_line


def extract_skills(text: str) -> list[str]:
    """
    Keyword-based skill extraction: checks which skills from SKILLS_DB
    appear in the text (case-insensitive, word-boundary aware so 'R' doesn't
    match inside 'Router', etc.)
    """
    found = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(text: str) -> list[str]:
    """Finds lines that mention common education keywords/degrees."""
    matches = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in EDUCATION_KEYWORDS):
            matches.append(line.strip())
    return matches


def extract_years_of_experience(text: str) -> int:
    """
    Looks for explicit mentions like '3 years' or '4+ years' and returns
    the highest number found. Returns 0 if none found (e.g. fresher resumes).
    """
    matches = EXPERIENCE_YEARS_REGEX.findall(text)
    years = [int(m) for m in matches]
    return max(years) if years else 0


# ---------------- MAIN PARSE FUNCTION ----------------

def parse_document(file_path: str) -> dict:
    """
    Runs the full pipeline on a single resume or JD file and returns
    a structured dictionary of extracted fields.
    """
    text = extract_text(file_path)
    return {
        "file_name": os.path.basename(file_path),
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "years_of_experience": extract_years_of_experience(text),
    }