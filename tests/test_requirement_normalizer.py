from app.matching.normalizer import RequirementNormalizer
from app.vocabulary.models import (
    VocabularyCategory,
    VocabularyConcept,
)
from app.vocabulary.repository import (
    InMemoryVocabularyRepository,
)


def create_vocabulary() -> InMemoryVocabularyRepository:
    return InMemoryVocabularyRepository(
        concepts=[
            VocabularyConcept(
                category=VocabularyCategory.SKILL,
                canonical_value="JavaScript",
                aliases=[
                    "JS",
                    "Java Script",
                ],
            ),
            VocabularyConcept(
                category=VocabularyCategory.SKILL,
                canonical_value="Kubernetes",
                aliases=[
                    "K8s",
                ],
            ),
            VocabularyConcept(
                category=VocabularyCategory.EDUCATION,
                canonical_value="Bachelor Degree",
                aliases=[
                    "Bachelor's Degree",
                    "Bachelor of Arts",
                    "Bachelor of Science",
                    "BA",
                    "BS",
                ],
            ),
        ]
    )


def test_normalizes_case_and_whitespace() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize(
        "  Machine   Learning  "
    ) == "machine learning"


def test_normalizes_curly_and_standard_apostrophes() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize(
        "Bachelor’s Degree"
    ) == "bachelors degree"

    assert normalizer.normalize(
        "Bachelor's Degree"
    ) == "bachelors degree"


def test_normalizes_hyphens_and_underscores() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize(
        "machine-learning"
    ) == "machine learning"

    assert normalizer.normalize(
        "machine_learning"
    ) == "machine learning"


def test_normalizes_ampersands() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize(
        "Research & Development"
    ) == "research and development"


def test_removes_unsupported_punctuation() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize(
        "Python, SQL, and Linux!"
    ) == "python sql and linux"


def test_preserves_meaningful_programming_characters() -> None:
    normalizer = RequirementNormalizer()

    assert normalizer.normalize("C++") == "c++"
    assert normalizer.normalize("C#") == "c#"
    assert normalizer.normalize("Node.js") == "node.js"


def test_does_not_resolve_vocabulary_without_category() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert normalizer.normalize("JS") == "js"


def test_resolves_alias_with_category() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    result = normalizer.normalize(
        "JS",
        VocabularyCategory.SKILL,
    )

    assert result == "javascript"


def test_resolves_canonical_value_with_category() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    result = normalizer.normalize(
        "JavaScript",
        VocabularyCategory.SKILL,
    )

    assert result == "javascript"


def test_recognizes_equivalent_skill_values() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert normalizer.equivalent(
        "JS",
        "JavaScript",
        VocabularyCategory.SKILL,
    )


def test_recognizes_equivalent_education_values() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert normalizer.equivalent(
        "Bachelor of Arts",
        "Bachelor's Degree",
        VocabularyCategory.EDUCATION,
    )


def test_category_prevents_invalid_cross_domain_resolution() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert normalizer.normalize(
        "BA",
        VocabularyCategory.SKILL,
    ) == "ba"

    assert normalizer.normalize(
        "BA",
        VocabularyCategory.EDUCATION,
    ) == "bachelor degree"


def test_unknown_value_falls_back_to_normalized_text() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert normalizer.normalize(
        "PyTorch",
        VocabularyCategory.SKILL,
    ) == "pytorch"


def test_values_are_not_equivalent_without_known_relationship() -> None:
    normalizer = RequirementNormalizer(
        vocabulary=create_vocabulary()
    )

    assert not normalizer.equivalent(
        "Python",
        "Java",
        VocabularyCategory.SKILL,
    )


def test_external_vocabulary_can_add_new_concepts() -> None:
    vocabulary = create_vocabulary()
    normalizer = RequirementNormalizer(vocabulary=vocabulary)

    vocabulary.add(
        VocabularyConcept(
            category=VocabularyCategory.SKILL,
            canonical_value="Amazon Web Services",
            aliases=["AWS"],
        )
    )

    assert normalizer.equivalent(
        "AWS",
        "Amazon Web Services",
        VocabularyCategory.SKILL,
    )