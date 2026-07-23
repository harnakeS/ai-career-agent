from app.models.job_requirements import (
    JobRequirements,
    Requirement,
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.duration import (
    extract_minimum_experience_months,
)
from app.parsing.requirements.schema import ExtractedJobRequirements


_IMPORTANCE_PRIORITY: dict[RequirementImportance, int] = {
    RequirementImportance.OPTIONAL: 1,
    RequirementImportance.PREFERRED: 2,
    RequirementImportance.REQUIRED: 3,
}
from app.vocabulary.text import normalize_vocabulary_text

def _normalize_alternatives(
    value: str,
    alternatives: list[str],
) -> list[str]:
    """Trim and deduplicate alternative requirement values."""

    normalized_primary = value.casefold()
    seen = {normalized_primary}
    result: list[str] = []

    for alternative in alternatives:
        cleaned_alternative = alternative.strip()
        normalized_alternative = cleaned_alternative.casefold()

        if (
            not cleaned_alternative
            or normalized_alternative in seen
        ):
            continue

        seen.add(normalized_alternative)
        result.append(cleaned_alternative)

    return result

def _expand_mixed_requirement(
    requirement: Requirement,
) -> list[Requirement]:
    """
    Separate a degree level from alternative fields of study.

    Small language models may incorrectly return a degree level and its
    acceptable academic fields as one alternatives group. A candidate
    must satisfy both the degree level and one acceptable field.
    """

    if (
        requirement.category
        != RequirementCategory.EDUCATION
        or len(requirement.alternatives) < 2
    ):
        return [requirement]

    normalized_value = normalize_vocabulary_text(
        requirement.value
    )

    education_level_terms = {
        "degree",
        "diploma",
        "ged",
    }

    value_is_education_level = any(
        term in normalized_value.split()
        for term in education_level_terms
    )

    if not value_is_education_level:
        return [requirement]

    alternatives_are_fields = all(
        not any(
            term
            in normalize_vocabulary_text(
                alternative
            ).split()
            for term in education_level_terms
        )
        for alternative in requirement.alternatives
    )

    if not alternatives_are_fields:
        return [requirement]

    degree_requirement = requirement.model_copy(
        update={
            "alternatives": [],
        }
    )

    field_requirement = Requirement(
        category=RequirementCategory.EDUCATION,
        importance=requirement.importance,
        value=requirement.alternatives[0],
        alternatives=requirement.alternatives[1:],
        source_text=requirement.source_text,
    )

    return [
        degree_requirement,
        field_requirement,
    ]


def convert_extracted_requirements(
    extracted: ExtractedJobRequirements,
) -> JobRequirements:
    """
    Convert validated LLM output into the application's canonical model.

    This conversion is profession-agnostic. It does not check requirements
    against a fixed vocabulary or alter domain-specific terminology.
    """

    deduplicated: dict[tuple[str, str], Requirement] = {}

    for extracted_requirement in extracted.requirements:
        value = extracted_requirement.value.strip()

        if not value:
            continue

        source_text = (
            extracted_requirement.source_text.strip()
            if extracted_requirement.source_text
            else ""
        )

        alternatives = _normalize_alternatives(
            value,
            extracted_requirement.alternatives,
        )

        deduplication_key = (
            extracted_requirement.category.value,
            value.casefold(),
        )

        requirement = Requirement(
            category=extracted_requirement.category,
            importance=extracted_requirement.importance,
            value=value,
            alternatives=alternatives,
            source_text=source_text,
        )

        expanded_requirements = (
            _expand_mixed_requirement(requirement)
        )

        for expanded_requirement in expanded_requirements:
            deduplication_key = (
                expanded_requirement.category.value,
                expanded_requirement.value.casefold(),
            )

            existing = deduplicated.get(
                deduplication_key
            )

            if existing is None:
                deduplicated[
                    deduplication_key
                ] = expanded_requirement
                continue

            if (
                _IMPORTANCE_PRIORITY[
                    expanded_requirement.importance
                ]
                > _IMPORTANCE_PRIORITY[
                    existing.importance
                ]
            ):
                deduplicated[
                    deduplication_key
                ] = expanded_requirement

    minimum_experience_months = extracted.minimum_experience_months

    if minimum_experience_months is None:
        extracted_durations = [
            extract_minimum_experience_months(requirement.value)
            for requirement in deduplicated.values()
            if requirement.category == RequirementCategory.EXPERIENCE
            ]

        valid_durations = [
            duration
            for duration in extracted_durations
            if duration is not None
            ]

        if valid_durations:
            minimum_experience_months = max(valid_durations)


    return JobRequirements(
        requirements=list(deduplicated.values()),
        minimum_experience_months=minimum_experience_months,
        entry_level=extracted.entry_level,
        work_authorization_required=extracted.work_authorization_required,
        sponsorship_available=extracted.sponsorship_available,
)