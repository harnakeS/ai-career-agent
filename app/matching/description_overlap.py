import re

from pydantic import BaseModel, Field

from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
)
from app.vocabulary.text import normalize_vocabulary_text


_SUPPORTED_CATEGORIES = {
    EvidenceCategory.SKILL,
    EvidenceCategory.EDUCATION,
    EvidenceCategory.CERTIFICATION,
    EvidenceCategory.LICENSE,
    EvidenceCategory.LANGUAGE,
}


class DescriptionEvidenceOverlap(BaseModel):
    """Candidate evidence explicitly mentioned in a job description."""

    evidence: CandidateEvidence
    reason: str


class DescriptionEvidenceOverlapResult(BaseModel):
    """All explicit candidate-evidence mentions found in a posting."""

    overlaps: list[DescriptionEvidenceOverlap] = Field(
        default_factory=list
    )


class DescriptionEvidenceOverlapMatcher:
    """
    Find candidate evidence explicitly mentioned in a job description.

    This is a deterministic overlap signal. It does not decide whether
    an occurrence is required, preferred, or sufficient for eligibility.
    """

    def match(
        self,
        description: str,
        evidence: CandidateEvidenceCollection,
    ) -> DescriptionEvidenceOverlapResult:
        normalized_description = normalize_vocabulary_text(
            description
        )

        overlaps: list[DescriptionEvidenceOverlap] = []
        seen: set[tuple[str, str]] = set()

        for item in evidence.evidence:
            if item.category not in _SUPPORTED_CATEGORIES:
                continue

            normalized_value = normalize_vocabulary_text(
                item.value
            )

            if not normalized_value:
                continue

            key = (
                item.category.value,
                normalized_value,
            )

            if key in seen:
                continue

            pattern = (
                rf"(?<![a-z0-9+#.])"
                rf"{re.escape(normalized_value)}"
                rf"(?![a-z0-9+#.])"
            )

            if not re.search(pattern, normalized_description):
                continue

            seen.add(key)

            overlaps.append(
                DescriptionEvidenceOverlap(
                    evidence=item,
                    reason=(
                        f"Candidate evidence '{item.value}' appears "
                        "explicitly in the job description."
                    ),
                )
            )

        return DescriptionEvidenceOverlapResult(
            overlaps=overlaps
        )