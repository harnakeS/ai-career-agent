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

def test_extracted_requirement_accepts_alternatives() -> None:
    requirement = ExtractedRequirement(
        category=RequirementCategory.SKILL,
        importance=RequirementImportance.REQUIRED,
        value="SQL",
        alternatives=["Python", "R"],
    )

    assert requirement.alternatives == ["Python", "R"]


def test_extracted_requirement_uses_empty_alternatives_by_default() -> None:
    requirement = ExtractedRequirement(
        category=RequirementCategory.SKILL,
        importance=RequirementImportance.REQUIRED,
        value="Python",
    )

    assert requirement.alternatives == []

def test_extracted_requirement_schema_describes_atomic_values() -> None:
    schema = ExtractedRequirement.model_json_schema()
    description = schema["properties"]["value"]["description"]

    assert "concise, atomic qualification" in description
    assert "degree with a field of study" in description
    assert "duration with an experience domain" in description


def test_extracted_requirement_schema_limits_alternatives() -> None:
    schema = ExtractedRequirement.model_json_schema()
    description = (
        schema["properties"]["alternatives"]["description"]
    )

    assert "same requirement category" in description
    assert "same" in description
    assert "qualification type" in description
    assert "another mandatory qualification" in description