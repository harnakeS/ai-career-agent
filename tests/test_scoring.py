import pytest
from app.matching.components import CategoryScore
from app.matching.scoring import (
    WeightedCategory,
    aggregate_scores,
    normalize_category_score,
)


def test_normalize_category_score_scales_to_target_maximum() -> None:
    result = CategoryScore(
        score=40.0,
        reasons=["Matched technologies."],
    )

    normalized = normalize_category_score(
        result,
        original_max=55.0,
        target_max=35.0,
    )

    assert normalized == pytest.approx(25.4545, rel=1e-4)


def test_normalize_category_score_caps_at_target_maximum() -> None:
    result = CategoryScore(
        score=80.0,
        reasons=[],
    )

    normalized = normalize_category_score(
        result,
        original_max=55.0,
        target_max=35.0,
    )

    assert normalized == 35.0


def test_normalize_category_score_rejects_invalid_original_max() -> None:
    result = CategoryScore(
        score=10.0,
        reasons=[],
    )

    with pytest.raises(
        ValueError,
        match="Original maximum must be greater than zero",
    ):
        normalize_category_score(
            result,
            original_max=0.0,
            target_max=10.0,
        )


def test_aggregate_scores_combines_categories() -> None:
    categories = [
        WeightedCategory(
            name="technical",
            result=CategoryScore(
                score=30.0,
                reasons=["Strong technical overlap."],
            ),
            max_points=35.0,
        ),
        WeightedCategory(
            name="experience",
            result=CategoryScore(
                score=15.0,
                reasons=["Relevant internship experience."],
            ),
            max_points=20.0,
        ),
        WeightedCategory(
            name="location",
            result=CategoryScore(
                score=5.0,
                reasons=["Preferred location."],
            ),
            max_points=5.0,
        ),
    ]

    result = aggregate_scores(categories)

    assert result.score == pytest.approx(83.3333, rel=1e-4)
    assert result.category_scores == {
        "technical": 30.0,
        "experience": 15.0,
        "location": 5.0,
    }
    assert result.reasons == [
        "Strong technical overlap.",
        "Relevant internship experience.",
        "Preferred location.",
    ]


def test_aggregate_scores_caps_total_at_100() -> None:
    categories = [
        WeightedCategory(
            name="technical",
            result=CategoryScore(
                score=70.0,
                reasons=[],
            ),
            max_points=70.0,
        ),
        WeightedCategory(
            name="experience",
            result=CategoryScore(
                score=50.0,
                reasons=[],
            ),
            max_points=50.0,
        ),
    ]

    result = aggregate_scores(categories)

    assert result.score == 100.0