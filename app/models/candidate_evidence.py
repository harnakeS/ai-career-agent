from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceCategory(StrEnum):
    SKILL = "skill"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    CERTIFICATION = "certification"
    LICENSE = "license"
    PROJECT = "project"
    LANGUAGE = "language"


class EvidenceSourceType(StrEnum):
    SKILLS = "skills"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    PROJECT = "project"
    CERTIFICATION = "certification"
    OTHER = "other"


class EvidenceConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CandidateEvidence(BaseModel):
    category: EvidenceCategory
    value: str = Field(min_length=1)
    source_type: EvidenceSourceType
    source_name: str = ""
    evidence_text: str = ""
    confidence: EvidenceConfidence = EvidenceConfidence.HIGH


class CandidateEvidenceCollection(BaseModel):
    evidence: list[CandidateEvidence] = Field(default_factory=list)

    def by_category(
        self,
        category: EvidenceCategory,
    ) -> list[CandidateEvidence]:
        return [
            item
            for item in self.evidence
            if item.category == category
        ]

    def by_source_type(
        self,
        source_type: EvidenceSourceType,
    ) -> list[CandidateEvidence]:
        return [
            item
            for item in self.evidence
            if item.source_type == source_type
        ]

    def find_value(
        self,
        value: str,
    ) -> list[CandidateEvidence]:
        normalized_value = value.strip().casefold()

        return [
            item
            for item in self.evidence
            if item.value.strip().casefold() == normalized_value
        ]