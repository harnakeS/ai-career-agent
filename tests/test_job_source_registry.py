import pytest

from app.job_sources.errors import (
    DuplicateJobSourceError,
    InvalidJobSourceImplementationError,
    JobSourceNotRegisteredError,
)
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)
from app.job_sources.registry import JobSourceRegistry


class StubJobSource:
    """Test-only implementation satisfying the JobSource protocol."""

    def collect(
        self,
        source: CompanySource,
    ) -> list[RawJobPosting]:
        return []


def test_registry_starts_empty() -> None:
    registry = JobSourceRegistry()

    assert registry.registered_providers == ()


def test_registers_and_returns_job_source() -> None:
    source = StubJobSource()
    registry = JobSourceRegistry()

    registry.register(
        JobSourceProvider.GREENHOUSE,
        source,
    )

    assert (
        registry.get(JobSourceProvider.GREENHOUSE)
        is source
    )


def test_accepts_initial_source_mapping() -> None:
    source = StubJobSource()

    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: source,
        }
    )

    assert (
        registry.get(JobSourceProvider.GREENHOUSE)
        is source
    )


def test_reports_registered_provider() -> None:
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: StubJobSource(),
        }
    )

    assert registry.contains(
        JobSourceProvider.GREENHOUSE
    )
    assert not registry.contains(
        JobSourceProvider.LEVER
    )


def test_returns_registered_providers_in_order() -> None:
    registry = JobSourceRegistry()

    registry.register(
        JobSourceProvider.GREENHOUSE,
        StubJobSource(),
    )
    registry.register(
        JobSourceProvider.LEVER,
        StubJobSource(),
    )

    assert registry.registered_providers == (
        JobSourceProvider.GREENHOUSE,
        JobSourceProvider.LEVER,
    )


def test_rejects_duplicate_provider_registration() -> None:
    registry = JobSourceRegistry()

    registry.register(
        JobSourceProvider.GREENHOUSE,
        StubJobSource(),
    )

    with pytest.raises(
        DuplicateJobSourceError,
        match="already registered",
    ):
        registry.register(
            JobSourceProvider.GREENHOUSE,
            StubJobSource(),
        )


def test_raises_when_provider_is_not_registered() -> None:
    registry = JobSourceRegistry()

    with pytest.raises(
        JobSourceNotRegisteredError,
        match="No job source is registered",
    ):
        registry.get(JobSourceProvider.WORKDAY)


def test_rejects_invalid_implementation() -> None:
    registry = JobSourceRegistry()

    with pytest.raises(
        InvalidJobSourceImplementationError,
        match="does not satisfy JobSource",
    ):
        registry.register(
            JobSourceProvider.GREENHOUSE,
            object(),  # type: ignore[arg-type]
        )