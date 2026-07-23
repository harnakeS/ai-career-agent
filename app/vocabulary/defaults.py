from app.vocabulary.models import (
    VocabularyCategory,
    VocabularyConcept,
)
from app.vocabulary.repository import (
    InMemoryVocabularyRepository,
)


DEFAULT_VOCABULARY_CONCEPTS = [
    VocabularyConcept(
        category=VocabularyCategory.EDUCATION,
        canonical_value="Bachelor Degree",
        aliases=[
            "Bachelor's Degree",
            "Bachelors Degree",
            "Bachelor of Arts",
            "Bachelor of Science",
            "BA",
            "B.A.",
            "BS",
            "B.S.",
        ],
    ),
    VocabularyConcept(
        category=VocabularyCategory.EDUCATION,
        canonical_value="Master Degree",
        aliases=[
            "Master's Degree",
            "Masters Degree",
            "Master of Arts",
            "Master of Science",
            "MA",
            "M.A.",
            "MS",
            "M.S.",
        ],
    ),
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
        canonical_value="Amazon Web Services",
        aliases=[
            "AWS",
        ],
    ),
    VocabularyConcept(
        category=VocabularyCategory.SKILL,
        canonical_value="Kubernetes",
        aliases=[
            "K8s",
        ],
    ),
]


def create_default_vocabulary_repository(
) -> InMemoryVocabularyRepository:
    """Create an independent repository containing default concepts."""

    return InMemoryVocabularyRepository(
        concepts=DEFAULT_VOCABULARY_CONCEPTS
    )