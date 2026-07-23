from enum import StrEnum

from pydantic import BaseModel, Field


class RequirementCategory(StrEnum):
    """Supported types of job requirements."""
    
    SKILL = "skill"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    CERTIFICATION = "certification"
    LICENSE = "license"
    SCHEDULE = "schedule"
    LOCATION = "location"
    LANGUAGE = "language"
    CLEARANCE = "clearance"
    AUTHORIZATION = "authorization"


class RequirementImportance(StrEnum):
    """How strongly the employer values a requirement."""

    REQUIRED = "required"
    PREFERRED = "preferred"
    OPTIONAL = "optional"


class Requirement(BaseModel):
    """One structured requirement extracted from a job posting."""

    category: RequirementCategory
    importance: RequirementImportance
    value: str
    alternatives: list[str] = Field(default_factory=list)
    source_text: str | None = None

    @property
    def acceptable_values(self) -> list[str]:
        """Return every value that can satisfy this requirement."""

        return [
            self.value,
            *self.alternatives,
        ]

class JobRequirements(BaseModel):
    """Structured requirements extracted from a job posting."""

    requirements: list[Requirement] = Field(default_factory=list)

    minimum_experience_months: int | None = None
    entry_level: bool = False
    work_authorization_required: bool = False
    sponsorship_available: bool | None = None

    def get_requirements(
        self,
        *,
        category: RequirementCategory | None = None,
        importance: RequirementImportance | None = None,
    ) -> list[Requirement]:
        """Return requirements filtered by category and importance."""

        return [
            requirement
            for requirement in self.requirements
            if (
                category is None
                or requirement.category == category
            )
            and (
                importance is None
                or requirement.importance == importance
            )
        ]

    def get_required(
        self,
        category: RequirementCategory | None = None,
    ) -> list[Requirement]:
        """Return required requirements, optionally filtered by category."""

        return self.get_requirements(
            category=category,
            importance=RequirementImportance.REQUIRED,
        )

    def get_preferred(
        self,
        category: RequirementCategory | None = None,
    ) -> list[Requirement]:
        """Return preferred requirements, optionally filtered by category."""

        return self.get_requirements(
            category=category,
            importance=RequirementImportance.PREFERRED,
        )