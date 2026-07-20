from collections.abc import Iterable
from typing import Protocol

from app.vocabulary.models import (
    VocabularyCategory,
    VocabularyConcept,
)
from app.vocabulary.text import normalize_vocabulary_text


class VocabularyRepository(Protocol):
    """Interface for resolving and storing vocabulary concepts."""

    def resolve(
        self,
        value: str,
        category: VocabularyCategory,
    ) -> str | None:
        """Return the canonical value, or None when no concept is known."""
        ...

    def add(self, concept: VocabularyConcept) -> None:
        """Add a vocabulary concept."""
        ...


class InMemoryVocabularyRepository:
    """
    In-memory vocabulary repository.

    This implementation is useful for tests and initial development. A future
    SQLite implementation can follow the same repository interface.
    """

    def __init__(
        self,
        concepts: Iterable[VocabularyConcept] | None = None,
    ) -> None:
        self._concepts: list[VocabularyConcept] = []
        self._lookup: dict[
            tuple[VocabularyCategory, str],
            str,
        ] = {}

        for concept in concepts or []:
            self.add(concept)

    def resolve(
        self,
        value: str,
        category: VocabularyCategory,
    ) -> str | None:
        normalized_value = normalize_vocabulary_text(value)

        if not normalized_value:
            return None

        return self._lookup.get(
            (category, normalized_value)
        )

    def add(self, concept: VocabularyConcept) -> None:
        normalized_canonical = normalize_vocabulary_text(
            concept.canonical_value
        )

        if not normalized_canonical:
            raise ValueError(
                "Vocabulary canonical value cannot be blank."
            )

        terms = [
            normalized_canonical,
            *(
                normalize_vocabulary_text(alias)
                for alias in concept.aliases
            ),
        ]

        for term in terms:
            if not term:
                continue

            key = (concept.category, term)
            existing_value = self._lookup.get(key)

            if (
                existing_value is not None
                and existing_value != normalized_canonical
            ):
                raise ValueError(
                    f"Vocabulary term '{term}' is already mapped to "
                    f"'{existing_value}' in category "
                    f"'{concept.category.value}'."
                )

            self._lookup[key] = normalized_canonical

        self._concepts.append(concept)

    def all(self) -> list[VocabularyConcept]:
        """Return a copy of all stored concepts."""

        return list(self._concepts)