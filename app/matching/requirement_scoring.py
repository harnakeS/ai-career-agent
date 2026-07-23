from dataclasses import dataclass

from app.matching.evidence_matcher import (
    EvidenceMatchResult,
)
from app.models.job_requirements import (
    RequirementImportance,
)


_REQUIREMENT_WEIGHTS = {
    RequirementImportance.REQUIRED: 5.0,
    RequirementImportance.PREFERRED: 2.0,
    RequirementImportance.OPTIONAL: 1.0,
}


@dataclass(frozen=True)
class RequirementCoverageScore:
    """Deterministic weighted coverage of extracted requirements."""

    score: float | None
    earned_points: float
    available_points: float
    evaluated_count: int
    unevaluated_count: int
    matched_required_count: int
    required_count: int
    matched_non_required_count: int
    non_required_count: int


class RequirementCoverageScorer:
    """Score evaluated requirement matches by employer importance."""

    def score(
        self,
        result: EvidenceMatchResult,
    ) -> RequirementCoverageScore:
        evaluated_matches = [
            match
            for match in result.matches
            if match.evaluated
        ]

        available_points = sum(
            _REQUIREMENT_WEIGHTS[
                match.requirement.importance
            ]
            for match in evaluated_matches
        )

        earned_points = sum(
            _REQUIREMENT_WEIGHTS[
                match.requirement.importance
            ]
            for match in evaluated_matches
            if match.matched
        )

        required_matches = [
            match
            for match in evaluated_matches
            if (
                match.requirement.importance
                == RequirementImportance.REQUIRED
            )
        ]

        non_required_matches = [
            match
            for match in evaluated_matches
            if (
                match.requirement.importance
                in {
                    RequirementImportance.PREFERRED,
                    RequirementImportance.OPTIONAL,
                }
            )
        ]

        if available_points == 0:
            score = None
        else:
            score = round(
                (
                    earned_points
                    / available_points
                )
                * 100.0,
                1,
            )

        return RequirementCoverageScore(
            score=score,
            earned_points=earned_points,
            available_points=available_points,
            evaluated_count=len(evaluated_matches),
            unevaluated_count=len(
                result.unevaluated_requirements
            ),
            matched_required_count=sum(
                1
                for match in required_matches
                if match.matched
            ),
            required_count=len(required_matches),
            matched_non_required_count=sum(
                1
                for match in non_required_matches
                if match.matched
            ),
            non_required_count=len(
                non_required_matches
            ),
        )