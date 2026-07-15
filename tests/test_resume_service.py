from pathlib import Path
from app.parsing.experience_parser import EmploymentType
from app.parsing.resume_parser import parse_resume


def test_parse_resume_combines_all_parser_steps(
    tmp_path: Path,
    monkeypatch,
) -> None:
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"placeholder")

    sample_text = """Harnake Sahi

EDUCATION
Bachelor of Arts in Computer Science
Sep 2022 - May 2026
Rutgers University

SKILLS
Programming Languages
Python | Java
Frameworks/Libraries
Pandas
Tools & Technologies
Git
Concepts
Machine Learning
Certifications
Azure AI Engineer Associate

WORK EXPERIENCE
Example Company
May 2025 - Sep 2025
Software Engineer Intern
New York, NY
• Built Python tools for internal workflows.

PROJECTS
AI Job Matching System
Jan 2026 - Mar 2026
Python, SQL
• Built a job recommendation system.
"""

    monkeypatch.setattr(
        "app.parsing.resume_parser.extract_pdf_text",
        lambda _: sample_text,
    )

    parsed_resume = parse_resume(resume_path)

    assert parsed_resume.raw_text == sample_text
    assert parsed_resume.education.degree == "Bachelor of Arts"
    assert parsed_resume.education.major == "Computer Science"
    assert parsed_resume.education.minor is None
    assert parsed_resume.education.institution == "Rutgers University"
    assert parsed_resume.education.graduation_year == 2026
    assert "Bachelor of Arts" in parsed_resume.sections.education
    assert parsed_resume.skills.programming_languages == [
        "Python",
        "Java",
    ]
    assert parsed_resume.skills.frameworks == ["Pandas"]
    assert parsed_resume.skills.tools == ["Git"]
    assert parsed_resume.skills.concepts == ["Machine Learning"]
    assert parsed_resume.skills.certifications == [
        "Azure AI Engineer Associate",
    ]
    assert len(parsed_resume.experiences) == 1

    experience = parsed_resume.experiences[0]

    assert experience.company == "Example Company"
    assert experience.title == "Software Engineer Intern"
    assert experience.employment_type == EmploymentType.INTERNSHIP
    assert experience.duration_months == 5
    assert experience.location == "New York, NY"
    assert experience.bullets == [
        "Built Python tools for internal workflows."
    ]
    assert len(parsed_resume.projects) == 1

    project = parsed_resume.projects[0]

    assert project.name == "AI Job Matching System"
    assert project.duration_months == 3
    assert project.technologies == ["Python", "SQL"]
    assert project.bullets == [
        "Built a job recommendation system."
    ]