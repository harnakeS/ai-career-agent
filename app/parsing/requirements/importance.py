from app.models.job_requirements import RequirementImportance


REQUIRED_PHRASES = (
    "required",
    "must have",
    "must possess",
    "minimum qualification",
    "minimum qualifications",
    "you must",
)

PREFERRED_PHRASES = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "desired",
)

OPTIONAL_PHRASES = (
    "optional",
    "not required",
)


def classify_requirement_importance(
    text: str,
) -> RequirementImportance:
    """Classify requirement importance using deterministic phrases."""

    normalized_text = text.lower().strip()

    if any(
        phrase in normalized_text
        for phrase in OPTIONAL_PHRASES
    ):
        return RequirementImportance.OPTIONAL

    if any(
        phrase in normalized_text
        for phrase in REQUIRED_PHRASES
    ):
        return RequirementImportance.REQUIRED

    if any(
        phrase in normalized_text
        for phrase in PREFERRED_PHRASES
    ):
        return RequirementImportance.PREFERRED

    return RequirementImportance.REQUIRED