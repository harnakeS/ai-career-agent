from collections.abc import Iterable

from pydantic import BaseModel, Field

from app.job_sources.converter import JobPostingConverter
from app.job_sources.errors import JobSourceError
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)
from app.job_sources.registry import JobSourceRegistry
from app.models.job import JobPosting


class CompanyCollectionFailure(BaseModel):
    """Expected failure encountered while collecting one company."""

    company_name: str
    provider: JobSourceProvider
    source_identifier: str
    error_type: str
    message: str


class CompanyCollectionResult(BaseModel):
    """Combined result of collecting multiple company sources."""

    jobs: list[JobPosting] = Field(default_factory=list)
    successful_sources: list[CompanySource] = Field(
        default_factory=list
    )
    skipped_sources: list[CompanySource] = Field(
        default_factory=list
    )
    failures: list[CompanyCollectionFailure] = Field(
        default_factory=list
    )


class CompanyJobCollectionService:
    """Collect and convert jobs from configured company sources."""

    def __init__(
        self,
        registry: JobSourceRegistry,
        converter: JobPostingConverter | None = None,
    ) -> None:
        self._registry = registry
        self._converter = converter or JobPostingConverter()

    def collect(
        self,
        sources: Iterable[CompanySource],
    ) -> CompanyCollectionResult:
        result = CompanyCollectionResult()

        for source in sources:
            if not source.enabled:
                result.skipped_sources.append(source)
                continue

            try:
                job_source = self._registry.get(
                    source.provider
                )
                raw_postings = job_source.collect(source)

                converted_jobs = [
                    self._converter.convert(raw_posting)
                    for raw_posting in raw_postings
                ]

            except JobSourceError as exc:
                result.failures.append(
                    CompanyCollectionFailure(
                        company_name=source.company_name,
                        provider=source.provider,
                        source_identifier=(
                            source.source_identifier
                        ),
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )
                continue

            result.jobs.extend(converted_jobs)
            result.successful_sources.append(source)

        return result