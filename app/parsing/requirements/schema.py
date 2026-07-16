from pydantic import BaseModel, Field

from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)


class ExtractedRequirement(BaseModel):
    """One requirement returned by the language model."""

    category: RequirementCategory
    importance: RequirementImportance
    value: str = Field(min_length=1)
    source_text: str | None = None


class ExtractedJobRequirements(BaseModel):
    """Validated structured output returned by the language model."""

    requirements: list[ExtractedRequirement] = Field(
        default_factory=list
    )
    minimum_experience_months: int | None = Field(
        default=None,
        ge=0,
    )
    entry_level: bool = False
    work_authorization_required: bool = False
    sponsorship_available: bool | None = None