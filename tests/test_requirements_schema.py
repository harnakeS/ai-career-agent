import pytest
from pydantic import ValidationError

from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)


def test_extracted_requirement_accepts_dynamic_skill() -> None:
    requirement = ExtractedRequirement(
        category=RequirementCategory.SKILL,
        importance=RequirementImportance.REQUIRED,
        value="A technology not stored in a vocabulary",
        source_text="Experience with this technology is required.",
    )

    assert requirement.value == (
        "A technology not stored in a vocabulary"
    )


def test_extracted_job_requirements_accepts_structured_output() -> None:
    result = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
            ),
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.PREFERRED,
                value="Apache Airflow",
            ),
        ],
        minimum_experience_months=24,
        entry_level=False,
    )

    assert len(result.requirements) == 2
    assert result.minimum_experience_months == 24


def test_extracted_requirement_rejects_empty_value() -> None:
    with pytest.raises(ValidationError):
        ExtractedRequirement(
            category=RequirementCategory.SKILL,
            importance=RequirementImportance.REQUIRED,
            value="",
        )


def test_extracted_requirements_reject_negative_experience() -> None:
    with pytest.raises(ValidationError):
        ExtractedJobRequirements(
            minimum_experience_months=-1,
        )