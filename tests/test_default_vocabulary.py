from app.matching.normalizer import RequirementNormalizer
from app.vocabulary.defaults import (
    create_default_vocabulary_repository,
)
from app.vocabulary.models import VocabularyCategory


def test_default_vocabulary_resolves_bachelor_degree() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_default_vocabulary_repository()
    )

    assert normalizer.equivalent(
        "Bachelor's Degree",
        "Bachelor of Arts",
        VocabularyCategory.EDUCATION,
    )


def test_default_vocabulary_resolves_skill_aliases() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_default_vocabulary_repository()
    )

    assert normalizer.equivalent(
        "AWS",
        "Amazon Web Services",
        VocabularyCategory.SKILL,
    )

    assert normalizer.equivalent(
        "K8s",
        "Kubernetes",
        VocabularyCategory.SKILL,
    )


def test_default_vocabulary_factory_returns_independent_repositories() -> None:
    first = create_default_vocabulary_repository()
    second = create_default_vocabulary_repository()

    assert first is not second
    assert first.all() == second.all()