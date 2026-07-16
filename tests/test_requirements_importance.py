import pytest

from app.models.job_requirements import RequirementImportance
from app.parsing.requirements.importance import (
    classify_requirement_importance,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Python experience is required.",
            RequirementImportance.REQUIRED,
        ),
        (
            "Candidates must have experience with SQL.",
            RequirementImportance.REQUIRED,
        ),
        (
            "Docker experience is preferred.",
            RequirementImportance.PREFERRED,
        ),
        (
            "Kubernetes knowledge is a nice-to-have.",
            RequirementImportance.PREFERRED,
        ),
        (
            "AWS certification is a plus.",
            RequirementImportance.PREFERRED,
        ),
        (
            "Azure certification is optional.",
            RequirementImportance.OPTIONAL,
        ),
        (
            "Security+ is not required.",
            RequirementImportance.OPTIONAL,
        ),
    ],
)
def test_classify_requirement_importance(
    text: str,
    expected: RequirementImportance,
) -> None:
    assert classify_requirement_importance(text) == expected


def test_classify_requirement_importance_defaults_to_required() -> None:
    result = classify_requirement_importance(
        "Experience with Python and SQL."
    )

    assert result == RequirementImportance.REQUIRED