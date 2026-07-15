from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSkills:
    """Structured skills extracted from a resume skills section."""

    programming_languages: list[str]
    frameworks: list[str]
    tools: list[str]
    concepts: list[str]
    certifications: list[str]


SKILL_HEADINGS = {
    "Programming Languages": "programming_languages",
    "Frameworks/Libraries": "frameworks",
    "Tools & Technologies": "tools",
    "Concepts": "concepts",
    "Certifications": "certifications",
}


def split_pipe_separated_values(value: str) -> list[str]:
    """Split a pipe-separated skill line into clean values."""
    return [
        item.strip()
        for item in value.split("|")
        if item.strip()
    ]


def parse_skills_section(text: str) -> ParsedSkills:
    """Parse a resume skills section into structured categories."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    parsed: dict[str, list[str]] = {
        "programming_languages": [],
        "frameworks": [],
        "tools": [],
        "concepts": [],
        "certifications": [],
    }

    current_category: str | None = None

    for line in lines:
        if line in SKILL_HEADINGS:
            current_category = SKILL_HEADINGS[line]
            continue

        if current_category is None:
            continue

        parsed[current_category].extend(
            split_pipe_separated_values(line)
        )

    return ParsedSkills(
        programming_languages=parsed["programming_languages"],
        frameworks=parsed["frameworks"],
        tools=parsed["tools"],
        concepts=parsed["concepts"],
        certifications=parsed["certifications"],
    )