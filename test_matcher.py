"""
Quick test script: ranks all sample resumes against one job description
so you can see the matching engine actually working end-to-end.

Run: python test_matcher.py
"""
import os
from src.matcher import rank_resumes_for_jd

RESUME_DIR = "data/sample_resumes"
JD_PATH = "data/sample_jds/jd_data_scientist.txt"

resume_paths = [
    os.path.join(RESUME_DIR, f) for f in os.listdir(RESUME_DIR)
]

print(f"Ranking resumes against: {JD_PATH}\n")
results = rank_resumes_for_jd(resume_paths, JD_PATH)

for i, r in enumerate(results, start=1):
    print(f"#{i} {r['resume_name']} ({r['resume_file']})")
    print(f"    Final Score: {r['final_score']}%  (skills: {r['skill_score']}%, semantic: {r['semantic_score']}%)")
    print(f"    Matched skills: {r['matched_skills']}")
    print(f"    Missing skills: {r['missing_skills']}")
    print()