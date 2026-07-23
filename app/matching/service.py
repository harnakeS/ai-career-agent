from dataclasses import dataclass

from app.matching.description_overlap import (
    DescriptionEvidenceOverlapMatcher,
    DescriptionEvidenceOverlapResult,
)
from app.matching.evidence_matcher import (
    EvidenceMatcher,
    EvidenceMatchResult,
)
from app.models.candidate_evidence import (
    CandidateEvidenceCollection,
)
from app.models.job import JobPosting
from app.models.job_requirements import (
    JobRequirements,
    RequirementImportance,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
)
from app.matching.requirement_scoring import (
    RequirementCoverageScore,
    RequirementCoverageScorer,
)


@dataclass(frozen=True)
class CandidateJobMatchResult:
    """Complete evidence-matching result for one candidate and job."""

    job: JobPosting
    requirements: JobRequirements
    evidence_matches: EvidenceMatchResult
    description_overlaps: DescriptionEvidenceOverlapResult
    coverage_score: RequirementCoverageScore
    requirements_cache_hit: bool = False

    @property
    def matched_count(self) -> int:
        return len(
            self.evidence_matches.matched_requirements
        )

    @property
    def unmatched_count(self) -> int:
        """Return all evaluated requirements without matching evidence."""

        return len(
            self.evidence_matches.unmatched_requirements
        )

    @property
    def required_gap_count(self) -> int:
        """Return unmatched requirements marked as required."""

        return sum(
            1
            for match in self.evidence_matches.matches
            if (
                match.evaluated
                and not match.matched
                and match.requirement.importance
                == RequirementImportance.REQUIRED
            )
        )

    @property
    def non_required_missing_count(self) -> int:
        """Return unmatched preferred and optional qualifications."""

        return sum(
            1
            for match in self.evidence_matches.matches
            if (
                match.evaluated
                and not match.matched
                and match.requirement.importance
                in {
                    RequirementImportance.PREFERRED,
                    RequirementImportance.OPTIONAL,
                }
            )
        )

    @property
    def unevaluated_count(self) -> int:
        return len(
            self.evidence_matches
            .unevaluated_requirements
        )

    @property
    def overlap_count(self) -> int:
        return len(self.description_overlaps.overlaps)


class CandidateJobMatchService:
    """Extract job requirements and match them to candidate evidence."""

    def __init__(
        self,
        requirements_service: RequirementsExtractionService,
        evidence_matcher: EvidenceMatcher | None = None,
        overlap_matcher: (
            DescriptionEvidenceOverlapMatcher | None
        ) = None,
        coverage_scorer: (
            RequirementCoverageScorer | None
        ) = None,
    ) -> None:
        self._requirements_service = requirements_service
        self._evidence_matcher = (
            evidence_matcher
            or EvidenceMatcher()
        )
        self._overlap_matcher = (
            overlap_matcher
            or DescriptionEvidenceOverlapMatcher()
        )
        self._coverage_scorer = (
            coverage_scorer
            or RequirementCoverageScorer()
        )

    def match(
        self,
        job: JobPosting,
        evidence: CandidateEvidenceCollection,
    ) -> CandidateJobMatchResult:
        """Extract and match requirements for one selected job."""

        extraction_result = (
            self._requirements_service
            .extract_with_metadata(job)
        )

        requirements = extraction_result.requirements

        evidence_matches = (
            self._evidence_matcher.match(
                requirements,
                evidence,
            )
        )

        coverage_score = (
            self._coverage_scorer.score(
                evidence_matches
            )
        )

        description_overlaps = (
            self._overlap_matcher.match(
                job.description,
                evidence,
            )
        )

        return CandidateJobMatchResult(
            job=job,
            requirements=requirements,
            evidence_matches=evidence_matches,
            description_overlaps=description_overlaps,
            coverage_score=coverage_score,
            requirements_cache_hit=(
                extraction_result.cache_hit
            ),
        )