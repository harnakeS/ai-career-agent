import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedEducation:
    """Structured education details extracted from a resume."""

    degree: str
    major: str
    minor: str | None
    institution: str
    graduation_year: int | None


def parse_education_section(text: str) -> ParsedEducation:
    """Parse a structured education section from resume text."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        raise ValueError("Education section does not contain enough information.")

    degree_line = lines[0]
    date_line = lines[1]
    institution = lines[2]

    minor: str | None = None
    major = degree_line
    degree = degree_line

    degree_match = re.match(
        r"(?P<degree>.+?) in (?P<major>.+?)(?:,\s*Minor in (?P<minor>.+))?$",
        degree_line,
        flags=re.IGNORECASE,
    )

    if degree_match:
        degree = degree_match.group("degree").strip()
        major = degree_match.group("major").strip()

        parsed_minor = degree_match.group("minor")
        if parsed_minor:
            minor = parsed_minor.strip()


    graduation_year: int | None = None

    full_year_matches = re.findall(r"\b(?:19|20)\d{2}\b", date_line)
    if full_year_matches:
        graduation_year = int(full_year_matches[-1])

    return ParsedEducation(
        degree=degree,
        major=major,
        minor=minor,
        institution=institution,
        graduation_year=graduation_year,
    )