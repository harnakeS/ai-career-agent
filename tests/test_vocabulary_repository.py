import pytest

from app.vocabulary.models import (
    VocabularyCategory,
    VocabularyConcept,
)
from app.vocabulary.repository import (
    InMemoryVocabularyRepository,
)


def create_javascript_concept() -> VocabularyConcept:
    return VocabularyConcept(
        category=VocabularyCategory.SKILL,
        canonical_value="JavaScript",
        aliases=[
            "JS",
            "Java Script",
        ],
    )


def test_resolves_canonical_value() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[create_javascript_concept()]
    )

    result = repository.resolve(
        "JavaScript",
        VocabularyCategory.SKILL,
    )

    assert result == "javascript"


def test_resolves_alias() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[create_javascript_concept()]
    )

    result = repository.resolve(
        "JS",
        VocabularyCategory.SKILL,
    )

    assert result == "javascript"


def test_resolution_is_case_insensitive() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[create_javascript_concept()]
    )

    result = repository.resolve(
        "JAVA SCRIPT",
        VocabularyCategory.SKILL,
    )

    assert result == "javascript"


def test_unknown_value_returns_none() -> None:
    repository = InMemoryVocabularyRepository()

    result = repository.resolve(
        "Python",
        VocabularyCategory.SKILL,
    )

    assert result is None


def test_same_alias_can_exist_in_different_categories() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[
            VocabularyConcept(
                category=VocabularyCategory.EDUCATION,
                canonical_value="Bachelor of Arts",
                aliases=["BA"],
            ),
            VocabularyConcept(
                category=VocabularyCategory.ROLE,
                canonical_value="Business Analyst",
                aliases=["BA"],
            ),
        ]
    )

    education_result = repository.resolve(
        "BA",
        VocabularyCategory.EDUCATION,
    )
    role_result = repository.resolve(
        "BA",
        VocabularyCategory.ROLE,
    )

    assert education_result == "bachelor of arts"
    assert role_result == "business analyst"


def test_conflicting_alias_in_same_category_raises_error() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[
            VocabularyConcept(
                category=VocabularyCategory.SKILL,
                canonical_value="JavaScript",
                aliases=["JS"],
            )
        ]
    )

    conflicting_concept = VocabularyConcept(
        category=VocabularyCategory.SKILL,
        canonical_value="Java Server",
        aliases=["JS"],
    )

    with pytest.raises(ValueError, match="already mapped"):
        repository.add(conflicting_concept)


def test_adds_concept_after_initialization() -> None:
    repository = InMemoryVocabularyRepository()

    repository.add(create_javascript_concept())

    assert repository.resolve(
        "JS",
        VocabularyCategory.SKILL,
    ) == "javascript"


def test_ignores_blank_aliases() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[
            VocabularyConcept(
                category=VocabularyCategory.SKILL,
                canonical_value="Python",
                aliases=["", "   ", "Py"],
            )
        ]
    )

    assert repository.resolve(
        "Py",
        VocabularyCategory.SKILL,
    ) == "python"

    assert repository.resolve(
        "",
        VocabularyCategory.SKILL,
    ) is None


def test_all_returns_stored_concepts() -> None:
    concept = create_javascript_concept()
    repository = InMemoryVocabularyRepository(
        concepts=[concept]
    )

    concepts = repository.all()

    assert concepts == [concept]


def test_all_returns_copy() -> None:
    repository = InMemoryVocabularyRepository(
        concepts=[create_javascript_concept()]
    )

    concepts = repository.all()
    concepts.clear()

    assert len(repository.all()) == 1