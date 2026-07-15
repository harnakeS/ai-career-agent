import pytest

from app.parsing.education_parser import parse_education_section


def test_parse_education_section_extracts_expected_fields() -> None:
    text = """Bachelor of Arts in Computer Science, Minor in Economics
Sep 2022 - May 2026
Rutgers University
New Brunswick, NJ
"""

    education = parse_education_section(text)

    assert education.degree == "Bachelor of Arts"
    assert education.major == "Computer Science"
    assert education.minor == "Economics"
    assert education.institution == "Rutgers University"
    assert education.graduation_year == 2026


def test_parse_education_section_supports_no_minor() -> None:
    text = """Bachelor of Science in Computer Science
Sep 2022 - May 2026
Example University
Example City, NJ
"""

    education = parse_education_section(text)

    assert education.degree == "Bachelor of Science"
    assert education.major == "Computer Science"
    assert education.minor is None
    assert education.graduation_year == 2026


def test_parse_education_section_uses_last_year_as_graduation_year() -> None:
    text = """Bachelor of Arts in Computer Science
Sep 2022 - May 2026
Rutgers University
"""

    education = parse_education_section(text)

    assert education.graduation_year == 2026


def test_parse_education_section_rejects_incomplete_input() -> None:
    with pytest.raises(
        ValueError,
        match="Education section does not contain enough information",
    ):
        parse_education_section("Bachelor of Arts in Computer Science")