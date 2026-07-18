import pytest

from app.parsing.requirements.duration import (
    extract_minimum_experience_months,
)


@pytest.mark.parametrize(
    ("text", "expected_months"),
    [
        ("At least 1 year of experience is required.", 12),
        ("Minimum 2 years of relevant experience.", 24),
        ("At least 6 months of warehouse experience.", 6),
        ("1.5 years of clinical experience preferred.", 18),
        ("No prior experience is required.", None),
    ],
)
def test_extract_minimum_experience_months(
    text: str,
    expected_months: int | None,
) -> None:
    result = extract_minimum_experience_months(text)

    assert result == expected_months