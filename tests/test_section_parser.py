import pytest

from app.parsing.resume.section_parser import split_resume_sections


SAMPLE_RESUME = """Harnake Sahi
example@email.com

EDUCATION
Bachelor of Arts in Computer Science
Rutgers University

SKILLS
Programming Languages
Python | Java | SQL

WORK EXPERIENCE
Example Company
Software Engineer Intern

PROJECTS
Job Matching System
Python | SQL
"""


def test_split_resume_sections_extracts_all_sections() -> None:
    sections = split_resume_sections(SAMPLE_RESUME)

    assert "Harnake Sahi" in sections.header
    assert "Bachelor of Arts" in sections.education
    assert "Python | Java | SQL" in sections.skills
    assert "Software Engineer Intern" in sections.work_experience
    assert "Job Matching System" in sections.projects


def test_split_resume_sections_removes_headings() -> None:
    sections = split_resume_sections(SAMPLE_RESUME)

    assert "EDUCATION" not in sections.education
    assert "SKILLS" not in sections.skills
    assert "WORK EXPERIENCE" not in sections.work_experience
    assert "PROJECTS" not in sections.projects


def test_split_resume_sections_rejects_missing_section() -> None:
    incomplete_resume = SAMPLE_RESUME.replace(
        "PROJECTS\nJob Matching System\nPython | SQL\n",
        "",
    )

    with pytest.raises(
        ValueError,
        match="Missing resume sections: PROJECTS",
    ):
        split_resume_sections(incomplete_resume)