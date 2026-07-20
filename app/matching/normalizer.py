from app.vocabulary.models import VocabularyCategory
from app.vocabulary.repository import VocabularyRepository
from app.vocabulary.text import normalize_vocabulary_text


class RequirementNormalizer:
    """
    Normalize requirement and evidence values.

    Generic formatting normalization is always applied. Concept resolution is
    performed through an injected vocabulary repository when both a repository
    and category are provided.
    """

    def __init__(
        self,
        vocabulary: VocabularyRepository | None = None,
    ) -> None:
        self._vocabulary = vocabulary

    def normalize(
        self,
        value: str,
        category: VocabularyCategory | None = None,
    ) -> str:
        """
        Return the normalized or canonical representation of a value.

        Without a vocabulary category, only generic text normalization is
        performed. Category-aware vocabulary resolution prevents ambiguous
        aliases from matching across unrelated domains.
        """

        normalized_value = self.normalize_text(value)

        if (
            not normalized_value
            or self._vocabulary is None
            or category is None
        ):
            return normalized_value

        canonical_value = self._vocabulary.resolve(
            normalized_value,
            category,
        )

        return canonical_value or normalized_value

    def equivalent(
        self,
        left: str,
        right: str,
        category: VocabularyCategory | None = None,
    ) -> bool:
        """Return whether two values resolve to the same concept."""

        return self.normalize(
            left,
            category,
        ) == self.normalize(
            right,
            category,
        )

    @staticmethod
    def normalize_text(value: str) -> str:
        """Apply generic text normalization without concept resolution."""

        return normalize_vocabulary_text(value)