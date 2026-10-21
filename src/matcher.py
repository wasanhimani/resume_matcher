"""
Matching engine: scores how well a resume matches a job description using
two combined signals:

1. Skill overlap — what fraction of the JD's required skills does the
   resume actually mention? (interpretable, easy to explain in a viva)
2. Semantic similarity — how close in *meaning* are the resume and JD
   overall, using sentence embeddings? (catches phrasing differences that
   pure keyword matching would miss, e.g. "built ML models" vs
   "machine learning experience")

The final score is a weighted combination of both.
"""
from sentence_transformers import SentenceTransformer, util

from src.parser import parse_document, extract_skills

# Loaded once and reused — downloads the model the first time this runs
# (needs internet access; cached locally afterwards).
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def compute_skill_match(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compares two skill lists and returns the overlap percentage, plus which
    skills matched and which required skills are missing from the resume.
    """
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)

    if not jd_set:
        return {"score": 0.0, "matched": [], "missing": []}

    matched = jd_set & resume_set
    missing = jd_set - resume_set

    score = len(matched) / len(jd_set)  # fraction of JD skills the resume covers

    return {
        "score": round(score * 100, 1),
        "matched": sorted(matched),
        "missing": sorted(missing),
    }


def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Encodes both texts into embeddings and returns cosine similarity,
    scaled to a 0-100 percentage.
    """
    model = get_model()
    embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    # cos_sim ranges roughly -1 to 1; clamp and scale to 0-100
    similarity = max(0.0, min(1.0, similarity))
    return round(similarity * 100, 1)


def match_resume_to_jd(resume_path: str, jd_path: str,
                        skill_weight: float = 0.6,
                        semantic_weight: float = 0.4) -> dict:
    """
    Runs the full matching pipeline for one resume against one JD and
    returns a structured result: overall score, breakdown, matched/missing
    skills, and both candidates' parsed info for display.
    """
    resume = parse_document(resume_path)
    jd = parse_document(jd_path)

    # The JD's own extracted "skills" field IS the set of required skills,
    # since extract_skills() runs on any text, JD or resume alike.
    skill_result = compute_skill_match(resume["skills"], jd["skills"])
    semantic_score = compute_semantic_similarity(resume["raw_text"], jd["raw_text"])

    final_score = round(
        skill_weight * skill_result["score"] + semantic_weight * semantic_score, 1
    )

    return {
        "resume_name": resume["name"] or resume["file_name"],
        "resume_file": resume["file_name"],
        "jd_file": jd["file_name"],
        "final_score": final_score,
        "skill_score": skill_result["score"],
        "semantic_score": semantic_score,
        "matched_skills": skill_result["matched"],
        "missing_skills": skill_result["missing"],
        "resume_years_experience": resume["years_of_experience"],
    }


def rank_resumes_for_jd(resume_paths: list[str], jd_path: str) -> list[dict]:
    """
    Screening use case: given many resumes and one JD, returns results
    sorted from best match to worst.
    """
    results = [match_resume_to_jd(path, jd_path) for path in resume_paths]
    return sorted(results, key=lambda r: r["final_score"], reverse=True)