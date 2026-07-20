from typing import Any

import pytest

from app.job_sources.errors import (
    InvalidJobSourceError,
    JobSourcePayloadError,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.http import JsonObject
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)
from app.job_sources.protocol import JobSource


class StubJsonHttpClient:
    """Test-only HTTP client that returns a predefined JSON payload."""

    def __init__(
        self,
        payload: JsonObject,
    ) -> None:
        self._payload = payload
        self.requested_urls: list[str] = []

    def get_json(
        self,
        url: str,
    ) -> JsonObject:
        self.requested_urls.append(url)
        return self._payload


def create_company_source(
    *,
    provider: JobSourceProvider = JobSourceProvider.GREENHOUSE,
    enabled: bool = True,
    source_identifier: str = "example-company",
) -> CompanySource:
    return CompanySource(
        company_name="Example Company",
        provider=provider,
        source_identifier=source_identifier,
        careers_url="https://example.com/careers",
        enabled=enabled,
    )


def create_greenhouse_job(
    *,
    external_id: int = 12345,
    title: str = "Software Engineer",
    location: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": external_id,
        "title": title,
        "updated_at": "2026-07-20T12:00:00Z",
        "location": location or {
            "name": "New York, NY",
        },
        "absolute_url": (
            f"https://boards.greenhouse.io/"
            f"example-company/jobs/{external_id}"
        ),
        "content": "Build and maintain software systems.",
    }


def test_greenhouse_source_satisfies_job_source_protocol() -> None:
    http_client = StubJsonHttpClient(
        payload={"jobs": []}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    assert isinstance(collector, JobSource)


def test_collect_maps_greenhouse_job_to_raw_posting() -> None:
    http_client = StubJsonHttpClient(
        payload={
            "jobs": [
                create_greenhouse_job(),
            ]
        }
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    result = collector.collect(
        create_company_source()
    )

    assert len(result) == 1

    posting = result[0]

    assert posting.external_id == "12345"
    assert posting.company_name == "Example Company"
    assert posting.title == "Software Engineer"
    assert posting.location == "New York, NY"
    assert (
        posting.description
        == "Build and maintain software systems."
    )
    assert posting.updated_at == "2026-07-20T12:00:00Z"
    assert (
        posting.source_provider
        == JobSourceProvider.GREENHOUSE
    )
    assert posting.source_identifier == "example-company"


def test_collect_uses_greenhouse_board_token_url() -> None:
    http_client = StubJsonHttpClient(
        payload={"jobs": []}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    collector.collect(
        create_company_source(
            source_identifier="example company",
        )
    )

    assert http_client.requested_urls == [
        (
            "https://boards-api.greenhouse.io/v1/boards/"
            "example%20company/jobs?content=true"
        )
    ]


def test_collect_returns_multiple_postings() -> None:
    http_client = StubJsonHttpClient(
        payload={
            "jobs": [
                create_greenhouse_job(
                    external_id=123,
                    title="Software Engineer",
                ),
                create_greenhouse_job(
                    external_id=456,
                    title="Data Engineer",
                ),
            ]
        }
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    result = collector.collect(
        create_company_source()
    )

    assert [posting.external_id for posting in result] == [
        "123",
        "456",
    ]
    assert [posting.title for posting in result] == [
        "Software Engineer",
        "Data Engineer",
    ]


def test_collect_returns_empty_list_when_source_disabled() -> None:
    http_client = StubJsonHttpClient(
        payload={
            "jobs": [
                create_greenhouse_job(),
            ]
        }
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    result = collector.collect(
        create_company_source(enabled=False)
    )

    assert result == []
    assert http_client.requested_urls == []


def test_collect_rejects_non_greenhouse_source() -> None:
    http_client = StubJsonHttpClient(
        payload={"jobs": []}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    with pytest.raises(
        InvalidJobSourceError,
        match="greenhouse provider",
    ):
        collector.collect(
            create_company_source(
                provider=JobSourceProvider.LEVER,
            )
        )


def test_collect_allows_missing_location() -> None:
    job = create_greenhouse_job()
    job["location"] = None

    http_client = StubJsonHttpClient(
        payload={"jobs": [job]}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    result = collector.collect(
        create_company_source()
    )

    assert result[0].location is None


def test_collect_rejects_payload_without_jobs_list() -> None:
    http_client = StubJsonHttpClient(
        payload={"jobs": "invalid"}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    with pytest.raises(
        JobSourcePayloadError,
        match="'jobs' list",
    ):
        collector.collect(
            create_company_source()
        )


def test_collect_rejects_job_without_external_id() -> None:
    job = create_greenhouse_job()
    del job["id"]

    http_client = StubJsonHttpClient(
        payload={"jobs": [job]}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    with pytest.raises(
        JobSourcePayloadError,
        match="missing its 'id'",
    ):
        collector.collect(
            create_company_source()
        )


def test_collect_rejects_job_without_application_url() -> None:
    job = create_greenhouse_job()
    del job["absolute_url"]

    http_client = StubJsonHttpClient(
        payload={"jobs": [job]}
    )
    collector = GreenhouseJobSource(
        http_client=http_client
    )

    with pytest.raises(
        JobSourcePayloadError,
        match="'absolute_url'",
    ):
        collector.collect(
            create_company_source()
        )