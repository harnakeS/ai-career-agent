import pytest
from pydantic import ValidationError

from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)


def test_creates_company_source() -> None:
    source = CompanySource(
        company_name="Example Company",
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier="example-company",
        careers_url="https://example.com/careers",
    )

    assert source.company_name == "Example Company"
    assert source.provider == JobSourceProvider.GREENHOUSE
    assert source.source_identifier == "example-company"
    assert source.enabled is True


def test_company_source_can_be_disabled() -> None:
    source = CompanySource(
        company_name="Example Company",
        provider=JobSourceProvider.LEVER,
        source_identifier="example-company",
        careers_url="https://example.com/jobs",
        enabled=False,
    )

    assert source.enabled is False


def test_company_source_requires_company_name() -> None:
    with pytest.raises(ValidationError):
        CompanySource(
            company_name="",
            provider=JobSourceProvider.GREENHOUSE,
            source_identifier="example-company",
            careers_url="https://example.com/careers",
        )


def test_company_source_requires_identifier() -> None:
    with pytest.raises(ValidationError):
        CompanySource(
            company_name="Example Company",
            provider=JobSourceProvider.GREENHOUSE,
            source_identifier="",
            careers_url="https://example.com/careers",
        )


def test_creates_raw_job_posting() -> None:
    posting = RawJobPosting(
        external_id="12345",
        company_name="Example Company",
        title="Software Engineer",
        location="New York, NY",
        description="Build and maintain software systems.",
        application_url="https://example.com/jobs/12345",
        published_at="2026-07-18T12:00:00Z",
        updated_at="2026-07-20T12:00:00Z",
        source_provider=JobSourceProvider.GREENHOUSE,
        source_identifier="example-company",
    )

    assert posting.external_id == "12345"
    assert posting.title == "Software Engineer"
    assert posting.source_provider == JobSourceProvider.GREENHOUSE
    assert posting.published_at == "2026-07-18T12:00:00Z"
    assert posting.updated_at == "2026-07-20T12:00:00Z"


def test_raw_job_posting_allows_unknown_location() -> None:
    posting = RawJobPosting(
        external_id="12345",
        company_name="Example Company",
        title="Software Engineer",
        description="Build and maintain software systems.",
        application_url="https://example.com/jobs/12345",
        source_provider=JobSourceProvider.GREENHOUSE,
        source_identifier="example-company",
    )

    assert posting.location is None
    assert posting.updated_at is None


def test_raw_job_posting_requires_external_id() -> None:
    with pytest.raises(ValidationError):
        RawJobPosting(
            external_id="",
            company_name="Example Company",
            title="Software Engineer",
            description="Build and maintain software systems.",
            application_url="https://example.com/jobs/12345",
            source_provider=JobSourceProvider.GREENHOUSE,
            source_identifier="example-company",
        )


def test_raw_job_posting_requires_valid_application_url() -> None:
    with pytest.raises(ValidationError):
        RawJobPosting(
            external_id="12345",
            company_name="Example Company",
            title="Software Engineer",
            description="Build and maintain software systems.",
            application_url="not-a-url",
            source_provider=JobSourceProvider.GREENHOUSE,
            source_identifier="example-company",
        )