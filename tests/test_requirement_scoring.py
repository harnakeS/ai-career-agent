from app.matching.evidence_matcher import (
    EvidenceMatchResult,
    RequirementMatch,
)
from app.matching.requirement_scoring import (
    RequirementCoverageScorer,
)
from app.models.job_requirements import (
    Requirement,
    RequirementCategory,
    RequirementImportance,
)


def create_match(
    *,
    importance: RequirementImportance,
    matched: bool,
    evaluated: bool = True,
    value: str = "Example requirement",
) -> RequirementMatch:
    return RequirementMatch(
        requirement=Requirement(
            category=RequirementCategory.SKILL,
            importance=importance,
            value=value,
            source_text=value,
        ),
        matched=matched,
        evaluated=evaluated,
        evidence=[],
        reason="Test requirement match.",
    )


def test_all_evaluated_requirements_matched_scores_100() -> None:
    result = EvidenceMatchResult(
        matches=[
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=True,
            ),
            create_match(
                importance=RequirementImportance.PREFERRED,
                matched=True,
            ),
            create_match(
                importance=RequirementImportance.OPTIONAL,
                matched=True,
            ),
        ]
    )

    score = RequirementCoverageScorer().score(
        result
    )

    assert score.score == 100.0
    assert score.earned_points == 8.0
    assert score.available_points == 8.0
    assert score.evaluated_count == 3


def test_weights_required_requirements_more_heavily() -> None:
    result = EvidenceMatchResult(
        matches=[
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=True,
                value="Python",
            ),
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=False,
                value="Three years experience",
            ),
            create_match(
                importance=RequirementImportance.PREFERRED,
                matched=True,
                value="AWS",
            ),
            create_match(
                importance=RequirementImportance.OPTIONAL,
                matched=False,
                value="Kubernetes",
            ),
        ]
    )

    score = RequirementCoverageScorer().score(
        result
    )

    assert score.earned_points == 7.0
    assert score.available_points == 13.0
    assert score.score == 53.8


def test_reports_required_and_non_required_counts() -> None:
    result = EvidenceMatchResult(
        matches=[
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=True,
            ),
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=False,
            ),
            create_match(
                importance=RequirementImportance.PREFERRED,
                matched=True,
            ),
            create_match(
                importance=RequirementImportance.OPTIONAL,
                matched=False,
            ),
        ]
    )

    score = RequirementCoverageScorer().score(
        result
    )

    assert score.matched_required_count == 1
    assert score.required_count == 2
    assert score.matched_non_required_count == 1
    assert score.non_required_count == 2


def test_excludes_unevaluated_requirements_from_score() -> None:
    result = EvidenceMatchResult(
        matches=[
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=True,
                value="Python",
            ),
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=False,
                evaluated=False,
                value="New York",
            ),
        ]
    )

    score = RequirementCoverageScorer().score(
        result
    )

    assert score.score == 100.0
    assert score.available_points == 5.0
    assert score.evaluated_count == 1
    assert score.unevaluated_count == 1


def test_returns_no_score_when_nothing_is_evaluated() -> None:
    result = EvidenceMatchResult(
        matches=[
            create_match(
                importance=RequirementImportance.REQUIRED,
                matched=False,
                evaluated=False,
            )
        ]
    )

    score = RequirementCoverageScorer().score(
        result
    )

    assert score.score is None
    assert score.earned_points == 0.0
    assert score.available_points == 0.0
    assert score.evaluated_count == 0
    assert score.unevaluated_count == 1


def test_empty_result_returns_no_score() -> None:
    score = RequirementCoverageScorer().score(
        EvidenceMatchResult()
    )

    assert score.score is None
    assert score.evaluated_count == 0
    assert score.unevaluated_count == 0