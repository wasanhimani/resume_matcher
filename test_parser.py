"""
Quick test script: runs the parsing pipeline on every sample resume
and prints the extracted structured data, so you can visually confirm
it's working correctly.

Run: python test_parser.py
"""
import os
from src.parser import parse_document

RESUME_DIR = "data/sample_resumes"

for filename in os.listdir(RESUME_DIR):
    file_path = os.path.join(RESUME_DIR, filename)
    result = parse_document(file_path)

    print("=" * 60)
    print(f"File: {result['file_name']}")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Years of Experience: {result['years_of_experience']}")
    print(f"Education: {result['education']}")
    print(f"Skills ({len(result['skills'])}): {result['skills']}")
    print()