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

        deduplication_key = (
            extracted_requirement.category.value,
            value.casefold(),
        )

        requirement = Requirement(
            category=extracted_requirement.category,
            importance=extracted_requirement.importance,
            value=value,
            source_text=source_text,
        )

        existing = deduplicated.get(deduplication_key)

        if existing is None:
            deduplicated[deduplication_key] = requirement
            continue

        if (
            _IMPORTANCE_PRIORITY[requirement.importance]
            > _IMPORTANCE_PRIORITY[existing.importance]
        ):
            deduplicated[deduplication_key] = requirement

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