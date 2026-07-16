import pytest

from app.parsing.resume.experience_parser import (
    EmploymentType,
    ParsedDateRange,
    calculate_duration_months,
    classify_employment_type,
    parse_date_range,
    parse_month_year,
    parse_experience_section,
)


def test_parse_month_year_with_abbreviated_month() -> None:
    month, year = parse_month_year("Sep 2025")

    assert month == 9
    assert year == 2025


def test_parse_month_year_with_full_month_name() -> None:
    month, year = parse_month_year("September 2025")

    assert month == 9
    assert year == 2025


def test_parse_month_year_without_month() -> None:
    month, year = parse_month_year("2025")

    assert month is None
    assert year == 2025


def test_parse_month_year_rejects_missing_year() -> None:
    with pytest.raises(
        ValueError,
        match="Could not find a year",
    ):
        parse_month_year("September")


def test_parse_date_range() -> None:
    date_range = parse_date_range("May 2025 - Sep 2025")

    assert date_range == ParsedDateRange(
        start_month=5,
        start_year=2025,
        end_month=9,
        end_year=2025,
    )


def test_calculate_duration_months_counts_inclusively() -> None:
    date_range = ParsedDateRange(
        start_month=5,
        start_year=2025,
        end_month=9,
        end_year=2025,
    )

    assert calculate_duration_months(date_range) == 5


def test_calculate_duration_months_returns_none_without_months() -> None:
    date_range = ParsedDateRange(
        start_month=None,
        start_year=2024,
        end_month=None,
        end_year=2025,
    )

    assert calculate_duration_months(date_range) is None


def test_calculate_duration_months_rejects_reversed_dates() -> None:
    date_range = ParsedDateRange(
        start_month=9,
        start_year=2025,
        end_month=5,
        end_year=2025,
    )

    with pytest.raises(
        ValueError,
        match="Experience end date occurs before start date",
    ):
        calculate_duration_months(date_range)

def test_classify_explicit_internship_title() -> None:
    result = classify_employment_type(
        "Software Engineering Intern",
    )

    assert result.employment_type == EmploymentType.INTERNSHIP
    assert result.confidence == 1.0
    assert "internship language" in result.reason


def test_classify_explicit_co_op_title() -> None:
    result = classify_employment_type(
        "Software Developer Co-op",
    )

    assert result.employment_type == EmploymentType.CO_OP
    assert result.confidence == 1.0


def test_classify_explicit_part_time_title() -> None:
    result = classify_employment_type(
        "Part-Time IT Support Specialist",
    )

    assert result.employment_type == EmploymentType.PART_TIME
    assert result.confidence == 1.0


def test_classify_explicit_contract_title() -> None:
    result = classify_employment_type(
        "Contract Software Developer",
    )

    assert result.employment_type == EmploymentType.CONTRACT
    assert result.confidence == 1.0


def test_classification_uses_manual_override() -> None:
    result = classify_employment_type(
        "WMS Solution Specialist",
        override=EmploymentType.INTERNSHIP,
    )

    assert result.employment_type == EmploymentType.INTERNSHIP
    assert result.confidence == 1.0
    assert result.reason == "Employment type was manually specified."


def test_classification_returns_unknown_when_title_is_ambiguous() -> None:
    result = classify_employment_type(
        "WMS Solution Specialist",
    )

    assert result.employment_type == EmploymentType.UNKNOWN
    assert result.confidence == 0.0

def test_parse_experience_section_extracts_multiple_roles() -> None:
    text = """Dropp Logistics
May 2025 - Sep 2025
WMS Solution Specialist
Dayton, NJ
• Improved warehouse workflows.
• Reduced inventory errors.

Dropp Logistics
May 2024 - Sep 2024
Supply Chain Intern
Dayton, NJ
• Built SQL dashboards.
• Automated reporting workflows.
"""

    experiences = parse_experience_section(
        text,
        employment_type_overrides={
            (
                "Dropp Logistics",
                "WMS Solution Specialist",
            ): EmploymentType.INTERNSHIP,
        },
    )

    assert len(experiences) == 2

    first = experiences[0]
    assert first.company == "Dropp Logistics"
    assert first.title == "WMS Solution Specialist"
    assert first.employment_type == EmploymentType.INTERNSHIP
    assert first.duration_months == 5
    assert first.location == "Dayton, NJ"
    assert first.bullets == [
        "Improved warehouse workflows.",
        "Reduced inventory errors.",
    ]

    second = experiences[1]
    assert second.title == "Supply Chain Intern"
    assert second.employment_type == EmploymentType.INTERNSHIP
    assert second.duration_months == 5
    assert second.bullets == [
        "Built SQL dashboards.",
        "Automated reporting workflows.",
    ]


def test_parse_experience_section_joins_wrapped_bullet_lines() -> None:
    text = """Example Company
May 2025 - Sep 2025
Software Engineering Intern
New York, NY
• Developed a Python data pipeline that processed
thousands of job records.
"""

    experiences = parse_experience_section(text)

    assert experiences[0].bullets == [
        (
            "Developed a Python data pipeline that processed "
            "thousands of job records."
        )
    ]


def test_parse_experience_section_rejects_invalid_entry_order() -> None:
    text = """Example Company
Software Engineering Intern
May 2025 - Sep 2025
New York, NY
"""

    with pytest.raises(
        ValueError,
        match="Expected date range after company",
    ):
        parse_experience_section(text)