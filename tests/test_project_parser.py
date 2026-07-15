import pytest

from app.parsing.project_parser import (
    parse_projects_section,
    parse_technology_line,
)


def test_parse_technology_line() -> None:
    technologies = parse_technology_line(
        "Python, Pandas, Scikit-learn"
    )

    assert technologies == [
        "Python",
        "Pandas",
        "Scikit-learn",
    ]


def test_parse_projects_section_extracts_multiple_projects() -> None:
    text = """NBA Match Predictor
Nov 2024 - Dec 2024
Python, Pandas, Scikit-learn
• Built a machine-learning pipeline.
• Improved prediction accuracy.

Inventory Management System
May 2025 - Sep 2025
SQL, Azure
• Built inventory-tracking workflows.
• Improved database performance.
"""

    projects = parse_projects_section(text)

    assert len(projects) == 2

    first = projects[0]
    assert first.name == "NBA Match Predictor"
    assert first.duration_months == 2
    assert first.technologies == [
        "Python",
        "Pandas",
        "Scikit-learn",
    ]
    assert first.bullets == [
        "Built a machine-learning pipeline.",
        "Improved prediction accuracy.",
    ]

    second = projects[1]
    assert second.name == "Inventory Management System"
    assert second.duration_months == 5
    assert second.technologies == ["SQL", "Azure"]
    assert second.bullets == [
        "Built inventory-tracking workflows.",
        "Improved database performance.",
    ]


def test_parse_projects_section_joins_wrapped_bullets() -> None:
    text = """AI Job Scout
Jan 2026 - Mar 2026
Python, SQL
• Built a recommendation pipeline that processed
thousands of job postings.
"""

    projects = parse_projects_section(text)

    assert projects[0].bullets == [
        (
            "Built a recommendation pipeline that processed "
            "thousands of job postings."
        )
    ]


def test_parse_projects_section_rejects_invalid_entry_order() -> None:
    text = """AI Job Scout
Python, SQL
Jan 2026 - Mar 2026
"""

    with pytest.raises(
        ValueError,
        match="Expected date range after project",
    ):
        parse_projects_section(text)