from pydantic import BaseModel, Field

from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
)
from app.models.job_requirements import (
    JobRequirements,
    Requirement,
    RequirementCategory,
)


class RequirementMatch(BaseModel):
    """Result of matching one job requirement against candidate evidence."""

    requirement: Requirement
    matched: bool
    evidence: list[CandidateEvidence] = Field(default_factory=list)
    reason: str


class EvidenceMatchResult(BaseModel):
    """Complete evidence-matching result for a job."""

    matches: list[RequirementMatch] = Field(default_factory=list)

    @property
    def matched_requirements(self) -> list[RequirementMatch]:
        return [match for match in self.matches if match.matched]

    @property
    def unmatched_requirements(self) -> list[RequirementMatch]:
        return [match for match in self.matches if not match.matched]


class EvidenceMatcher:
    """Match structured job requirements against candidate evidence."""

    _CATEGORY_MAP: dict[RequirementCategory, EvidenceCategory] = {
        RequirementCategory.SKILL: EvidenceCategory.SKILL,
        RequirementCategory.EDUCATION: EvidenceCategory.EDUCATION,
        RequirementCategory.EXPERIENCE: EvidenceCategory.EXPERIENCE,
        RequirementCategory.CERTIFICATION: EvidenceCategory.CERTIFICATION,
        RequirementCategory.LICENSE: EvidenceCategory.LICENSE,
        RequirementCategory.LANGUAGE: EvidenceCategory.LANGUAGE,
    }

    def match(
        self,
        requirements: JobRequirements,
        evidence: CandidateEvidenceCollection,
    ) -> EvidenceMatchResult:
        matches = [
            self.match_requirement(requirement, evidence)
            for requirement in requirements.requirements
        ]

        return EvidenceMatchResult(matches=matches)

    def match_requirement(
        self,
        requirement: Requirement,
        evidence: CandidateEvidenceCollection,
    ) -> RequirementMatch:
        evidence_category = self._CATEGORY_MAP.get(requirement.category)

        if evidence_category is None:
            return RequirementMatch(
                requirement=requirement,
                matched=False,
                evidence=[],
                reason=(
                    f"Requirement category '{requirement.category.value}' "
                    "is not supported by candidate evidence matching."
                ),
            )

        candidates = evidence.by_category(evidence_category)
        normalized_requirement = self._normalize(requirement.value)

        matching_evidence = [
            item
            for item in candidates
            if self._normalize(item.value) == normalized_requirement
        ]

        if matching_evidence:
            return RequirementMatch(
                requirement=requirement,
                matched=True,
                evidence=matching_evidence,
                reason=(
                    f"Found {len(matching_evidence)} matching candidate "
                    f"evidence item(s) for '{requirement.value}'."
                ),
            )

        return RequirementMatch(
            requirement=requirement,
            matched=False,
            evidence=[],
            reason=(
                f"No matching candidate evidence was found for "
                f"'{requirement.value}'."
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize text for deterministic exact-value matching."""

        return " ".join(value.casefold().split())