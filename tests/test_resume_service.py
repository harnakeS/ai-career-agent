from pathlib import Path

from app.resume.resume_parser import parse_resume


def test_parse_resume_combines_all_parser_steps(
    tmp_path: Path,
    monkeypatch,
) -> None:
    resume_path = tmp_path / "resume.pdf"
    resume_path.write_bytes(b"placeholder")

    sample_text = """Harnake Sahi

EDUCATION
Bachelor of Arts in Computer Science

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
Software Engineer Intern

PROJECTS
AI Job Matching System
Python | SQL
"""

    monkeypatch.setattr(
        "app.resume.resume_parser.extract_pdf_text",
        lambda _: sample_text,
    )

    parsed_resume = parse_resume(resume_path)

    assert parsed_resume.raw_text == sample_text
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