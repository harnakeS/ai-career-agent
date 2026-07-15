from app.resume.skills_parser import (
    parse_skills_section,
    split_pipe_separated_values,
)


SAMPLE_SKILLS_SECTION = """Programming Languages
Java | Python | C | SQL
Frameworks/Libraries
Pandas | BeautifulSoup | Scikit-learn
Tools & Technologies
Git | Linux | Azure
Concepts
Object-Oriented Programming | Machine Learning
Certifications
Azure AI Engineer Associate
"""


def test_split_pipe_separated_values() -> None:
    values = split_pipe_separated_values(
        "Java | Python | SQL"
    )

    assert values == ["Java", "Python", "SQL"]


def test_split_pipe_separated_values_removes_empty_items() -> None:
    values = split_pipe_separated_values(
        "Java |  | Python |"
    )

    assert values == ["Java", "Python"]


def test_parse_skills_section_extracts_categories() -> None:
    skills = parse_skills_section(SAMPLE_SKILLS_SECTION)

    assert skills.programming_languages == [
        "Java",
        "Python",
        "C",
        "SQL",
    ]

    assert skills.frameworks == [
        "Pandas",
        "BeautifulSoup",
        "Scikit-learn",
    ]

    assert skills.tools == [
        "Git",
        "Linux",
        "Azure",
    ]

    assert skills.concepts == [
        "Object-Oriented Programming",
        "Machine Learning",
    ]

    assert skills.certifications == [
        "Azure AI Engineer Associate",
    ]


def test_parse_skills_section_ignores_unknown_text_before_heading() -> None:
    text = """Technical Skills Summary
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
"""

    skills = parse_skills_section(text)

    assert skills.programming_languages == ["Python", "Java"]