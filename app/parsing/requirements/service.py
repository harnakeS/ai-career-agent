from app.models.job import JobPosting
from app.models.job_requirements import JobRequirements
from app.parsing.requirements.converter import (
    convert_extracted_requirements,
)
from app.parsing.requirements.extractor import RequirementsExtractor


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

        return convert_extracted_requirements(extracted)