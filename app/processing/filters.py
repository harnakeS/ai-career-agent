import re

from app.models.job import JobPosting


EXCLUDED_TITLE_TERMS = {
    "senior",
    "staff",
    "principal",
    "director",
    "vice president",
    "manager",
    "architect",
    "lead engineer",
}


def title_is_excluded(title: str) -> bool:
    """Return True when a title clearly indicates a senior-level role."""
    normalized_title = title.lower()

    return any(
        excluded_term in normalized_title
        for excluded_term in EXCLUDED_TITLE_TERMS
    )


def extract_minimum_experience(description: str) -> int | None:
    """Extract the lowest explicit experience requirement from a description."""
    normalized_description = description.lower()

    patterns = [
        r"(\d+)\+?\s+years? of experience",
        r"at least\s+(\d+)\s+years?",
        r"minimum of\s+(\d+)\s+years?",
        r"minimum\s+(\d+)\s+years?",
    ]

    experience_values: list[int] = []

    for pattern in patterns:
        matches = re.findall(pattern, normalized_description)
        experience_values.extend(int(match) for match in matches)

    return min(experience_values) if experience_values else None


def is_potential_match(job: JobPosting) -> tuple[bool, str]:
    """
    Apply basic eligibility rules.

    Returns:
        A tuple containing:
        - whether the job should continue through the pipeline
        - a short explanation
    """
    if title_is_excluded(job.title):
        return False, "Excluded because the title appears senior-level."

    minimum_experience = extract_minimum_experience(job.description)

    if minimum_experience is not None and minimum_experience >= 5:
        return (
            False,
            f"Excluded because the posting requests at least "
            f"{minimum_experience} years of experience.",
        )

    if minimum_experience is not None:
        return (
            True,
            f"Potential match with an identified requirement of "
            f"{minimum_experience} years.",
        )

    return True, "Potential match; no clear minimum experience requirement found."