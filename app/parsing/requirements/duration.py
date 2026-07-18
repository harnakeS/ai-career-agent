import re

_YEAR_PATTERN = re.compile(
    r"\b(?:at least\s+|minimum of\s+|minimum\s+)?"
    r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten)"
    r"\s*\+?\s*years?\b",
    re.IGNORECASE,
)

_MONTH_PATTERN = re.compile(
    r"\b(?:at least\s+|minimum of\s+|minimum\s+)?"
    r"(\d+)\s*\+?\s*months?\b",
    re.IGNORECASE,
)

_NUMBER_WORDS: dict[str, float] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def extract_minimum_experience_months(
    text: str,
) -> int | None:
    """Extract a minimum experience duration from requirement text."""

    month_match = _MONTH_PATTERN.search(text)

    if month_match:
        return int(month_match.group(1))

    year_match = _YEAR_PATTERN.search(text)

    if year_match:
        raw_years = year_match.group(1).casefold()

        if raw_years in _NUMBER_WORDS:
            years = _NUMBER_WORDS[raw_years]
        else:
            years = float(raw_years)

        return round(years * 12)

    return None