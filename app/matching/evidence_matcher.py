from pydantic import BaseModel, Field

from app.matching.normalizer import RequirementNormalizer
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
from app.parsing.requirements.duration import (
    extract_minimum_experience_months,
)
from app.vocabulary.models import VocabularyCategory


class RequirementMatch(BaseModel):
    """Result of matching one job requirement against candidate evidence."""

    requirement: Requirement
    matched: bool
    evidence: list[CandidateEvidence] = Field(default_factory=list)
    reason: str
    evaluated: bool = True


class EvidenceMatchResult(BaseModel):
    """Complete evidence-matching result for a job."""

    matches: list[RequirementMatch] = Field(default_factory=list)

    @property
    def matched_requirements(self) -> list[RequirementMatch]:
        return [match for match in self.matches if match.matched]

    @property
    def unmatched_requirements(
        self,
    ) -> list[RequirementMatch]:
        return [
            match
            for match in self.matches
            if match.evaluated and not match.matched
        ]
    
    @property
    def unevaluated_requirements(
        self,
    ) -> list[RequirementMatch]:
        return [
            match
            for match in self.matches
            if not match.evaluated
        ]

class EvidenceMatcher:
    """Match structured job requirements against candidate evidence."""

    _EVIDENCE_CATEGORY_MAP: dict[
        RequirementCategory,
        EvidenceCategory,
    ] = {
        RequirementCategory.SKILL: EvidenceCategory.SKILL,
        RequirementCategory.EDUCATION: EvidenceCategory.EDUCATION,
        RequirementCategory.EXPERIENCE: EvidenceCategory.EXPERIENCE,
        RequirementCategory.CERTIFICATION: EvidenceCategory.CERTIFICATION,
        RequirementCategory.LICENSE: EvidenceCategory.LICENSE,
        RequirementCategory.LANGUAGE: EvidenceCategory.LANGUAGE,
    }

    _VOCABULARY_CATEGORY_MAP: dict[
        RequirementCategory,
        VocabularyCategory,
    ] = {
        RequirementCategory.SKILL: VocabularyCategory.SKILL,
        RequirementCategory.EDUCATION: VocabularyCategory.EDUCATION,
        RequirementCategory.EXPERIENCE: VocabularyCategory.EXPERIENCE,
        RequirementCategory.CERTIFICATION: (
            VocabularyCategory.CERTIFICATION
        ),
        RequirementCategory.LICENSE: VocabularyCategory.LICENSE,
        RequirementCategory.LANGUAGE: VocabularyCategory.LANGUAGE,
    }

    def __init__(
        self,
        normalizer: RequirementNormalizer | None = None,
    ) -> None:
        self._normalizer = normalizer or RequirementNormalizer()

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
        evidence_category = self._EVIDENCE_CATEGORY_MAP.get(
            requirement.category
        )
        vocabulary_category = self._VOCABULARY_CATEGORY_MAP.get(
            requirement.category
        )

        if evidence_category is None or vocabulary_category is None:
            return RequirementMatch(
                requirement=requirement,
                matched=False,
                evaluated=False,
                evidence=[],
                reason=(
                    f"Requirement category "
                    f"'{requirement.category.value}' is not supported "
                    "by candidate evidence matching."
                ),
            )

        candidates = evidence.by_category(evidence_category)

        if requirement.category == RequirementCategory.EXPERIENCE:
            duration_match = self._match_experience_duration(
                requirement=requirement,
                candidates=candidates,
            )

            if duration_match is not None:
                return duration_match

        match_pairs: list[
            tuple[str, CandidateEvidence]
        ] = []

        for acceptable_value in requirement.acceptable_values:
            for item in candidates:
                if self._normalizer.equivalent(
                    acceptable_value,
                    item.value,
                    vocabulary_category,
                ):
                    match_pairs.append(
                        (acceptable_value, item)
                    )

        matching_evidence: list[CandidateEvidence] = []

        for _, item in match_pairs:
            if item not in matching_evidence:
                matching_evidence.append(item)

        if not matching_evidence:
            acceptable_values = ", ".join(
                f"'{value}'"
                for value in requirement.acceptable_values
            )

            return RequirementMatch(
                requirement=requirement,
                matched=False,
                evidence=[],
                reason=(
                    "No equivalent candidate evidence was found for "
                    f"any acceptable value: {acceptable_values}."
                ),
            )

        direct_match_pairs = [
            (acceptable_value, item)
            for acceptable_value, item in match_pairs
            if (
                self._normalizer.normalize_text(item.value)
                == self._normalizer.normalize_text(
                    acceptable_value
                )
            )
        ]

        if direct_match_pairs:
            matched_value = direct_match_pairs[0][0]

            if (
                self._normalizer.normalize_text(matched_value)
                == self._normalizer.normalize_text(
                    requirement.value
                )
            ):
                matched_value_description = (
                    f"'{requirement.value}'"
                )
            else:
                matched_value_description = (
                    f"alternative '{matched_value}' for "
                    f"'{requirement.value}'"
                )

            reason = (
                f"Found {len(matching_evidence)} matching candidate "
                "evidence item(s) using normalized direct-value "
                f"comparison with {matched_value_description}."
            )
        else:
            matched_value = match_pairs[0][0]
            canonical_value = self._normalizer.normalize(
                matched_value,
                vocabulary_category,
            )

            if (
                self._normalizer.normalize_text(matched_value)
                == self._normalizer.normalize_text(
                    requirement.value
                )
            ):
                matched_value_description = (
                    f"'{requirement.value}'"
                )
            else:
                matched_value_description = (
                    f"alternative '{matched_value}' for "
                    f"'{requirement.value}'"
                )

            reason = (
                f"Found {len(matching_evidence)} matching candidate "
                f"evidence item(s) for {matched_value_description} "
                "through the canonical vocabulary concept "
                f"'{canonical_value}'."
            )
        
        return RequirementMatch(
            requirement=requirement,
            matched=True,
            evidence=matching_evidence,
            reason=reason,
        )

    def _match_experience_duration(
        self,
        requirement: Requirement,
        candidates: list[CandidateEvidence],
    ) -> RequirementMatch | None:
        """
        Match a duration-based experience requirement.

        Returns None when the requirement does not contain a recognizable
        duration, allowing ordinary normalized matching to continue.
        """

        required_months = extract_minimum_experience_months(
            requirement.value
        )

        if required_months is None:
            return None

        evidence_with_duration: list[
            tuple[CandidateEvidence, int]
        ] = []

        for item in candidates:
            months = extract_minimum_experience_months(item.value)

            if months is None:
                continue

            evidence_with_duration.append((item, months))

        total_candidate_months = sum(
            months
            for _, months in evidence_with_duration
        )

        if total_candidate_months >= required_months:
            supporting_evidence = [
                item
                for item, _ in evidence_with_duration
            ]

            return RequirementMatch(
                requirement=requirement,
                matched=True,
                evidence=supporting_evidence,
                reason=(
                    f"Candidate evidence provides "
                    f"{total_candidate_months} month(s) of experience, "
                    f"meeting the requirement of "
                    f"{required_months} month(s)."
                ),
            )

        return RequirementMatch(
            requirement=requirement,
            matched=False,
            evidence=[],
            reason=(
                f"Candidate evidence provides "
                f"{total_candidate_months} month(s) of experience, "
                f"below the requirement of "
                f"{required_months} month(s)."
            ),
        )