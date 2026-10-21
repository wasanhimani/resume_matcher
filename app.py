"""
Streamlit web app for the Resume Screening & Job Matching System.

Two modes:
1. Screen resumes: upload one JD + multiple resumes, get a ranked list
   (the "recruiter" use case).
2. Match a single resume: upload one resume + one JD, get a detailed
   breakdown (the "job seeker" use case).

Run: streamlit run app.py
"""
import os
import tempfile

import streamlit as st

from src.parser import parse_document
from src.matcher import match_resume_to_jd, rank_resumes_for_jd

st.set_page_config(page_title="Resume Screening & Job Matching", layout="wide")

st.title("📄 Resume Screening & Job Matching System")
st.caption("NLP-based matching using skill extraction + semantic similarity")


def save_uploaded_file(uploaded_file) -> str:
    """Streamlit gives us an in-memory file; our parser needs a real path
    on disk, so we save it to a temp file and return that path."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def score_badge(score: float) -> str:
    if score >= 70:
        return f":green[**{score}%**]"
    elif score >= 40:
        return f":orange[**{score}%**]"
    else:
        return f":red[**{score}%**]"


mode = st.radio(
    "What do you want to do?",
    ["Screen multiple resumes against one job", "Match one resume against one job"],
    horizontal=True,
)

st.divider()

# ---------------- MODE 1: SCREENING (many resumes -> one JD) ----------------
if mode == "Screen multiple resumes against one job":
    col1, col2 = st.columns(2)

    with col1:
        jd_file = st.file_uploader("Upload Job Description (.txt, .pdf, .docx)",
                                    type=["txt", "pdf", "docx"], key="jd_screen")
    with col2:
        resume_files = st.file_uploader("Upload Resumes (.pdf, .docx)",
                                         type=["pdf", "docx"],
                                         accept_multiple_files=True, key="resumes_screen")

    if st.button("Rank Resumes", type="primary"):
        if not jd_file or not resume_files:
            st.warning("Please upload a job description and at least one resume.")
        else:
            with st.spinner("Parsing and matching..."):
                jd_path = save_uploaded_file(jd_file)
                resume_paths = [save_uploaded_file(f) for f in resume_files]
                results = rank_resumes_for_jd(resume_paths, jd_path)

            st.subheader(f"Results — {len(results)} candidate(s) ranked")

            for i, r in enumerate(results, start=1):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**#{i}. {r['resume_name']}** ({r['resume_file']})")
                        st.progress(r["final_score"] / 100)
                    with c2:
                        st.markdown(f"Overall: {score_badge(r['final_score'])}", unsafe_allow_html=False)
                        st.caption(f"Skills: {r['skill_score']}% · Semantic: {r['semantic_score']}%")

                    mc1, mc2 = st.columns(2)
                    with mc1:
                        st.markdown("✅ **Matched skills**")
                        st.write(", ".join(r["matched_skills"]) or "—")
                    with mc2:
                        st.markdown("❌ **Missing skills**")
                        st.write(", ".join(r["missing_skills"]) or "—")

# ---------------- MODE 2: SINGLE MATCH (one resume -> one JD) ----------------
else:
    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("Upload Resume (.pdf, .docx)",
                                        type=["pdf", "docx"], key="resume_single")
    with col2:
        jd_file = st.file_uploader("Upload Job Description (.txt, .pdf, .docx)",
                                    type=["txt", "pdf", "docx"], key="jd_single")

    if st.button("Check Match", type="primary"):
        if not resume_file or not jd_file:
            st.warning("Please upload both a resume and a job description.")
        else:
            with st.spinner("Parsing and matching..."):
                resume_path = save_uploaded_file(resume_file)
                jd_path = save_uploaded_file(jd_file)
                r = match_resume_to_jd(resume_path, jd_path)

            st.subheader(f"Match result for {r['resume_name']}")
            st.markdown(f"### Overall Match: {score_badge(r['final_score'])}")
            st.progress(r["final_score"] / 100)
            st.caption(f"Skill overlap: {r['skill_score']}%  |  Semantic similarity: {r['semantic_score']}%")

            mc1, mc2 = st.columns(2)
            with mc1:
                st.markdown("✅ **Matched skills**")
                for s in r["matched_skills"]:
                    st.write(f"- {s}")
            with mc2:
                st.markdown("❌ **Skills you're missing**")
                for s in r["missing_skills"]:
                    st.write(f"- {s}")

st.divider()
st.caption("Final Year Project — Resume Screening and Job Matching System using NLP")
