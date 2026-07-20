import pytest

from app.job_sources.collection import (
    CompanyJobCollectionService,
)
from app.job_sources.errors import JobSourceRequestError
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)
from app.job_sources.registry import JobSourceRegistry


class RecordingJobSource:
    """Test source with configurable postings and expected failures."""

    def __init__(
        self,
        postings_by_identifier: dict[
            str,
            list[RawJobPosting],
        ] | None = None,
        failures_by_identifier: dict[
            str,
            JobSourceRequestError,
        ] | None = None,
    ) -> None:
        self._postings_by_identifier = (
            postings_by_identifier or {}
        )
        self._failures_by_identifier = (
            failures_by_identifier or {}
        )
        self.collected_sources: list[CompanySource] = []

    def collect(
        self,
        source: CompanySource,
    ) -> list[RawJobPosting]:
        self.collected_sources.append(source)

        failure = self._failures_by_identifier.get(
            source.source_identifier
        )

        if failure is not None:
            raise failure

        return list(
            self._postings_by_identifier.get(
                source.source_identifier,
                [],
            )
        )


def create_company_source(
    *,
    company_name: str = "Example Company",
    provider: JobSourceProvider = JobSourceProvider.GREENHOUSE,
    source_identifier: str = "example-company",
    enabled: bool = True,
) -> CompanySource:
    return CompanySource(
        company_name=company_name,
        provider=provider,
        source_identifier=source_identifier,
        careers_url="https://example.com/careers",
        enabled=enabled,
    )


def create_raw_posting(
    *,
    external_id: str = "12345",
    company_name: str = "Example Company",
    description: str = "Build and maintain software systems.",
) -> RawJobPosting:
    return RawJobPosting(
        external_id=external_id,
        company_name=company_name,
        title="Software Engineer",
        location="New York, NY",
        description=description,
        application_url=(
            f"https://example.com/jobs/{external_id}"
        ),
        source_provider=JobSourceProvider.GREENHOUSE,
        source_identifier=company_name.casefold(),
    )


def test_collects_and_converts_jobs_from_one_company() -> None:
    company = create_company_source()
    job_source = RecordingJobSource(
        postings_by_identifier={
            "example-company": [
                create_raw_posting(),
            ]
        }
    )
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: job_source,
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([company])

    assert len(result.jobs) == 1
    assert result.jobs[0].requisition_id == "12345"
    assert result.successful_sources == [company]
    assert result.skipped_sources == []
    assert result.failures == []


def test_collects_multiple_companies_using_same_provider() -> None:
    first_company = create_company_source(
        company_name="First Company",
        source_identifier="first-company",
    )
    second_company = create_company_source(
        company_name="Second Company",
        source_identifier="second-company",
    )
    job_source = RecordingJobSource(
        postings_by_identifier={
            "first-company": [
                create_raw_posting(
                    external_id="111",
                    company_name="First Company",
                )
            ],
            "second-company": [
                create_raw_posting(
                    external_id="222",
                    company_name="Second Company",
                )
            ],
        }
    )
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: job_source,
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([
        first_company,
        second_company,
    ])

    assert {
        job.requisition_id
        for job in result.jobs
    } == {"111", "222"}
    assert result.successful_sources == [
        first_company,
        second_company,
    ]


def test_resolves_different_provider_implementations() -> None:
    greenhouse_company = create_company_source(
        company_name="Greenhouse Company",
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier="greenhouse-company",
    )
    lever_company = create_company_source(
        company_name="Lever Company",
        provider=JobSourceProvider.LEVER,
        source_identifier="lever-company",
    )

    greenhouse_source = RecordingJobSource(
        postings_by_identifier={
            "greenhouse-company": [
                create_raw_posting(
                    external_id="111",
                    company_name="Greenhouse Company",
                )
            ]
        }
    )
    lever_source = RecordingJobSource(
        postings_by_identifier={
            "lever-company": [
                create_raw_posting(
                    external_id="222",
                    company_name="Lever Company",
                )
            ]
        }
    )

    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: greenhouse_source,
            JobSourceProvider.LEVER: lever_source,
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([
        greenhouse_company,
        lever_company,
    ])

    assert {
        job.requisition_id
        for job in result.jobs
    } == {"111", "222"}
    assert greenhouse_source.collected_sources == [
        greenhouse_company
    ]
    assert lever_source.collected_sources == [
        lever_company
    ]


def test_skips_disabled_company_without_resolving_it() -> None:
    company = create_company_source(
        enabled=False
    )
    service = CompanyJobCollectionService(
        JobSourceRegistry()
    )

    result = service.collect([company])

    assert result.jobs == []
    assert result.successful_sources == []
    assert result.skipped_sources == [company]
    assert result.failures == []


def test_records_unregistered_provider_failure() -> None:
    company = create_company_source(
        provider=JobSourceProvider.WORKDAY
    )
    service = CompanyJobCollectionService(
        JobSourceRegistry()
    )

    result = service.collect([company])

    assert result.jobs == []
    assert len(result.failures) == 1
    assert (
        result.failures[0].error_type
        == "JobSourceNotRegisteredError"
    )
    assert result.failures[0].company_name == "Example Company"


def test_source_failure_does_not_stop_other_companies() -> None:
    failing_company = create_company_source(
        company_name="Failing Company",
        source_identifier="failing-company",
    )
    successful_company = create_company_source(
        company_name="Successful Company",
        source_identifier="successful-company",
    )
    job_source = RecordingJobSource(
        postings_by_identifier={
            "successful-company": [
                create_raw_posting(
                    external_id="222",
                    company_name="Successful Company",
                )
            ]
        },
        failures_by_identifier={
            "failing-company": JobSourceRequestError(
                "Provider request failed."
            )
        },
    )
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: job_source,
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([
        failing_company,
        successful_company,
    ])

    assert len(result.jobs) == 1
    assert result.jobs[0].requisition_id == "222"
    assert result.successful_sources == [
        successful_company
    ]
    assert len(result.failures) == 1
    assert (
        result.failures[0].company_name
        == "Failing Company"
    )


def test_conversion_failure_discards_company_snapshot() -> None:
    company = create_company_source()
    job_source = RecordingJobSource(
        postings_by_identifier={
            "example-company": [
                create_raw_posting(
                    external_id="111"
                ),
                create_raw_posting(
                    external_id="222",
                    description="<p>   </p>",
                ),
            ]
        }
    )
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: job_source,
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([company])

    assert result.jobs == []
    assert result.successful_sources == []
    assert len(result.failures) == 1
    assert (
        result.failures[0].error_type
        == "JobPostingConversionError"
    )


def test_empty_source_is_successful_collection() -> None:
    company = create_company_source()
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: (
                RecordingJobSource()
            ),
        }
    )
    service = CompanyJobCollectionService(registry)

    result = service.collect([company])

    assert result.jobs == []
    assert result.successful_sources == [company]
    assert result.failures == []


def test_collecting_no_sources_returns_empty_result() -> None:
    service = CompanyJobCollectionService(
        JobSourceRegistry()
    )

    result = service.collect([])

    assert result.jobs == []
    assert result.successful_sources == []
    assert result.skipped_sources == []
    assert result.failures == []


def test_unexpected_programming_error_is_not_suppressed() -> None:
    class BrokenJobSource:
        def collect(
            self,
            source: CompanySource,
        ) -> list[RawJobPosting]:
            raise RuntimeError("Unexpected implementation bug.")

    company = create_company_source()
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: BrokenJobSource(),
        }
    )
    service = CompanyJobCollectionService(registry)

    with pytest.raises(
        RuntimeError,
        match="Unexpected implementation bug",
    ):
        service.collect([company])