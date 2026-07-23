from dataclasses import dataclass

from app.models.job import JobPosting
from app.models.job_requirements import JobRequirements
from app.parsing.requirements.converter import (
    convert_extracted_requirements,
)
from app.parsing.requirements.extractor import (
    RequirementsExtractor,
)


@dataclass(frozen=True)
class RequirementsExtractionResult:
    """Requirements plus information about how they were obtained."""

    requirements: JobRequirements
    cache_hit: bool


class RequirementsExtractionService:
    """Coordinates requirement extraction and deterministic conversion."""

    def __init__(
        self,
        extractor: RequirementsExtractor,
    ) -> None:
        self._extractor = extractor

    def extract(
        self,
        job: JobPosting,
    ) -> JobRequirements:
        extracted = self._extractor.extract(job)

        return convert_extracted_requirements(
            extracted
        )

    def extract_with_metadata(
        self,
        job: JobPosting,
    ) -> RequirementsExtractionResult:
        """Extract requirements and report that no cache was used."""

        return RequirementsExtractionResult(
            requirements=self.extract(job),
            cache_hit=False,
        )