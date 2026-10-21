"""
A curated list of common technical skills used for keyword-based extraction
from resumes and job descriptions. Organized by category for readability,
but exposed as a single flat set (SKILLS_DB) for matching.

You can extend this list any time — the more complete it is, the better
your skill extraction will be. This is intentionally a simple, transparent
approach so you can explain exactly how it works in your viva.
"""

PROGRAMMING_LANGUAGES = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C", "C#", "Go",
    "Rust", "Kotlin", "Swift", "PHP", "Ruby", "R", "Scala", "MATLAB", "SQL",
]

WEB_FRAMEWORKS = [
    "React", "Angular", "Vue", "Vue.js", "Django", "Flask", "FastAPI",
    "Spring Boot", "Spring", "Express", "Express.js", "Node.js", "Next.js",
    "Redux", "jQuery", "Bootstrap", "Tailwind CSS", "HTML", "CSS",
]

DATA_ML = [
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
    "Computer Vision", "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
    "PyTorch", "Keras", "OpenCV", "XGBoost", "Data Analysis", "Data Visualization",
    "Statistics", "Data Science", "spaCy", "Matplotlib", "Seaborn", "Tableau",
    "Power BI",
]

DATABASES = [
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Redis",
    "Cassandra", "DynamoDB", "Firebase", "Elasticsearch",
]

DEVOPS_CLOUD = [
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
    "CI/CD", "Terraform", "Ansible", "Linux", "Git", "GitHub", "GitLab",
    "REST APIs", "REST", "GraphQL", "Microservices", "Nginx",
]

OTHER = [
    "Agile", "Scrum", "JIRA", "Data Structures", "Algorithms",
    "Object Oriented Programming", "OOP", "System Design", "Testing",
    "Unit Testing", "Selenium",
]

SKILLS_DB = sorted(set(
    PROGRAMMING_LANGUAGES + WEB_FRAMEWORKS + DATA_ML + DATABASES
    + DEVOPS_CLOUD + OTHER
))