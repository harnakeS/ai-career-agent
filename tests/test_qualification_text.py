from app.parsing.requirements.qualification_text import (
    extract_qualification_text,
)


def test_extracts_required_and_preferred_sections() -> None:
    description = """
**What You’ll Do:**

- Build dashboards.
- Prepare reports.

**Who You Are:**

- Bachelor's degree in computer science.
- Experience using SQL or Python.

**Bonus Points:**

- Experience with financial modeling.
- CFA certification is preferred.

**Benefits and Growth:**

- Competitive health benefits.
""".strip()

    result = extract_qualification_text(description)

    assert "**Who You Are:**" in result
    assert "Bachelor's degree" in result
    assert "SQL or Python" in result
    assert "**Bonus Points:**" in result
    assert "financial modeling" in result
    assert "CFA certification" in result

    assert "Build dashboards" not in result
    assert "Prepare reports" not in result
    assert "Competitive health benefits" not in result


def test_extracts_hash_style_qualification_heading() -> None:
    description = """
## Responsibilities

- Manage warehouse operations.

## Minimum Qualifications

- Two years of logistics experience.
- Forklift certification.

## About the Company

We provide logistics services.
""".strip()

    result = extract_qualification_text(description)

    assert "Minimum Qualifications" in result
    assert "Two years of logistics experience" in result
    assert "Forklift certification" in result
    assert "Manage warehouse operations" not in result
    assert "About the Company" not in result


def test_preserves_multiple_qualification_sections() -> None:
    description = """
**Required Qualifications:**

- Active RN license.

**Preferred Qualifications:**

- BLS certification.
- Acute-care experience.

**Benefits:**

- Paid time off.
""".strip()

    result = extract_qualification_text(description)

    assert "Active RN license" in result
    assert "BLS certification" in result
    assert "Acute-care experience" in result
    assert "Paid time off" not in result


def test_returns_full_description_without_known_heading() -> None:
    description = (
        "Applicants must have a driver's license and "
        "at least one year of delivery experience."
    )

    result = extract_qualification_text(description)

    assert result == description


def test_empty_description_returns_empty_text() -> None:
    assert extract_qualification_text("   ") == ""