from app.models.candidate import CandidateProfile


candidate = CandidateProfile(
    name="Harnake Sahi",
    years_experience=1,
    graduation_year=2026,
    education="B.A. Computer Science",
    majors=[
        "Computer Science",
        "Economics",
    ],
    skills=[
        "Machine Learning",
        "SQL",
        "Linux",
        "Git",
        "Data Structures",
        "Algorithms",
    ],
    programming_languages=[
        "Python",
        "Java",
        "C",
        "SQL",
    ],
    frameworks=[
        "Pandas",
        "BeautifulSoup",
        "Playwright",
        "Scikit-learn",
        "NumPy",
    ],
    tools=[
        "Azure",
        "Git",
        "Linux",
    ],
    certifications=[
        "Azure AI Engineer Associate",
    ],
    preferred_locations=[
        "New Jersey",
        "New York",
        "Remote",
    ],
    willing_to_relocate=True,
    us_citizen=True,
    desired_roles=[
        "Software Engineer",
        "Backend Engineer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Application Support Engineer",
    ],
)