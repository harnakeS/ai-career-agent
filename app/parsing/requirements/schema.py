from pydantic import BaseModel, Field

from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)


class ExtractedRequirement(BaseModel):
    """One requirement returned by the language model."""

    category: RequirementCategory
    importance: RequirementImportance
    value: str = Field(
        min_length=1,
        description=(
            "One concise, atomic qualification. The value must not "
            "combine a degree with a field of study, a duration with "
            "an experience domain, or a competency with a tool."
        ),
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description=(
            "Interchangeable one-of values that have the same "
            "requirement category and qualification type as value. "
            "An alternative must be able to replace value without "
            "removing another mandatory qualification."
        ),
    )
    source_text: str | None = Field(
        default=None,
        description=(
            "The complete original job-description text supporting "
            "this requirement."
        ),
    )


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