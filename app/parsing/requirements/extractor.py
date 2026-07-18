from typing import Protocol

from app.models.job import JobPosting
from app.parsing.requirements.schema import ExtractedJobRequirements


class RequirementsExtractor(Protocol):
    """Contract for extracting structured requirements from a job posting."""

    def extract(
        self,
        job: JobPosting,
    ) -> ExtractedJobRequirements:
        """Extract structured requirements from a job posting."""
        ...


class StubRequirementsExtractor:
    """Deterministic extractor used for tests and local development."""

    def __init__(
        self,
        result: ExtractedJobRequirements,
    ) -> None:
        self._result = result

    def extract(
        self,
        job: JobPosting,
    ) -> ExtractedJobRequirements:
        """Return the configured extraction result."""

        return self._result