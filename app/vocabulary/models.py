from enum import StrEnum

from pydantic import BaseModel, Field


class VocabularyCategory(StrEnum):
    """Domain category used to prevent ambiguous alias matches."""

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
    ROLE = "role"
    OTHER = "other"


class VocabularyConcept(BaseModel):
    """One canonical concept and its known alternative representations."""

    category: VocabularyCategory
    canonical_value: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)