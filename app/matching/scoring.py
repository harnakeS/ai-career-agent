from dataclasses import dataclass

from app.matching.components import CategoryScore


@dataclass(frozen=True)
class WeightedCategory:
    """One matching category and its contribution to the score."""

    name: str
    result: CategoryScore
    max_points: float
    applicable: bool = True


@dataclass(frozen=True)
class AggregatedScore:
    """Final score produced from weighted matching categories."""

    score: float
    category_scores: dict[str, float]
    reasons: list[str]


def normalize_category_score(
    result: CategoryScore,
    *,
    original_max: float,
    target_max: float,
) -> float:
    """Scale a category score from its original range to a new maximum."""

    if original_max <= 0:
        raise ValueError("Original maximum must be greater than zero.")

    normalized = (result.score / original_max) * target_max

    return max(0.0, min(normalized, target_max))


def aggregate_scores(
    categories: list[WeightedCategory],
) -> AggregatedScore:
    """Calculate a percentage using only applicable categories."""

    applicable_categories = [
        category
        for category in categories
        if category.applicable
    ]

    earned_points = sum(
        category.result.score
        for category in applicable_categories
    )

    available_points = sum(
        category.max_points
        for category in applicable_categories
    )

    if available_points == 0:
        final_score = 0.0
    else:
        final_score = (earned_points / available_points) * 100.0

    category_scores = {
        category.name: category.result.score
        for category in applicable_categories
    }

    reasons = [
        reason
        for category in applicable_categories
        for reason in category.result.reasons
    ]

    return AggregatedScore(
        score=max(0.0, min(final_score, 100.0)),
        category_scores=category_scores,
        reasons=reasons,
    )