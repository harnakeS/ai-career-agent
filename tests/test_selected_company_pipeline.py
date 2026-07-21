from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base, JobRecord
from app.job_sources.collection import (
    CompanyJobCollectionService,
)
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)
from app.job_sources.registry import JobSourceRegistry
from app.pipeline.selected_company_pipeline import (
    SelectedCompanyPipeline,
)


class ConfigurableJobSource:
    """Test source returning postings by source identifier."""

    def __init__(
        self,
        postings: dict[str, list[RawJobPosting]],
    ) -> None:
        self._postings = postings

    def collect(
        self,
        source: CompanySource,
    ) -> list[RawJobPosting]:
        return list(
            self._postings.get(
                source.source_identifier,
                [],
            )
        )


@pytest.fixture
def database() -> Iterator[
    tuple[Engine, sessionmaker[Session]]
]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    yield engine, session_factory

    engine.dispose()


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
    company_name: str = "Example Company",
    external_id: str = "12345",
    title: str = "Software Engineer",
    source_identifier: str = "example-company",
) -> RawJobPosting:
    return RawJobPosting(
        external_id=external_id,
        company_name=company_name,
        title=title,
        location="New York, NY",
        description="Build and maintain software systems.",
        application_url=(
            f"https://example.com/jobs/{external_id}"
        ),
        source_provider=JobSourceProvider.GREENHOUSE,
        source_identifier=source_identifier,
    )


def create_pipeline(
    *,
    postings: dict[str, list[RawJobPosting]],
    session_factory: sessionmaker[Session],
) -> SelectedCompanyPipeline:
    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: (
                ConfigurableJobSource(postings)
            )
        }
    )
    collection_service = CompanyJobCollectionService(
        registry=registry
    )

    return SelectedCompanyPipeline(
        collection_service=collection_service,
        session_factory=session_factory,
    )


def count_records(
    session_factory: sessionmaker[Session],
) -> int:
    with session_factory() as session:
        return session.scalar(
            select(func.count()).select_from(JobRecord)
        ) or 0


def test_runs_collection_and_persistence(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    source = create_company_source()
    pipeline = create_pipeline(
        postings={
            "example-company": [
                create_raw_posting(),
            ]
        },
        session_factory=session_factory,
    )

    result = pipeline.run([source])

    assert result.collected_jobs == 1
    assert result.new_jobs == 1
    assert result.updated_jobs == 0
    assert result.successful_collections == 1
    assert result.collection_failures == 0
    assert result.persistence_failures == 0
    assert count_records(session_factory) == 1
    assert result.deactivated_jobs == 0


def test_repeated_run_updates_without_duplicate(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    source = create_company_source()
    pipeline = create_pipeline(
        postings={
            "example-company": [
                create_raw_posting(),
            ]
        },
        session_factory=session_factory,
    )

    first_result = pipeline.run([source])
    second_result = pipeline.run([source])

    assert first_result.new_jobs == 1
    assert first_result.updated_jobs == 0
    assert second_result.new_jobs == 0
    assert second_result.updated_jobs == 1
    assert count_records(session_factory) == 1


def test_skips_disabled_company(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    source = create_company_source(enabled=False)
    pipeline = create_pipeline(
        postings={},
        session_factory=session_factory,
    )

    result = pipeline.run([source])

    assert result.collected_jobs == 0
    assert result.successful_collections == 0
    assert result.skipped_sources == 1
    assert result.collection_failures == 0
    assert result.persistence_failures == 0
    assert count_records(session_factory) == 0


def test_reports_unregistered_provider_failure(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    source = create_company_source(
        provider=JobSourceProvider.WORKDAY
    )
    collection_service = CompanyJobCollectionService(
        registry=JobSourceRegistry()
    )
    pipeline = SelectedCompanyPipeline(
        collection_service=collection_service,
        session_factory=session_factory,
    )

    result = pipeline.run([source])

    assert result.collected_jobs == 0
    assert result.collection_failures == 1
    assert result.new_jobs == 0
    assert result.persistence_failures == 0
    assert count_records(session_factory) == 0


def test_runs_multiple_company_sources(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    first_source = create_company_source(
        company_name="First Company",
        source_identifier="first-company",
    )
    second_source = create_company_source(
        company_name="Second Company",
        source_identifier="second-company",
    )
    pipeline = create_pipeline(
        postings={
            "first-company": [
                create_raw_posting(
                    company_name="First Company",
                    external_id="111",
                    source_identifier="first-company",
                )
            ],
            "second-company": [
                create_raw_posting(
                    company_name="Second Company",
                    external_id="222",
                    source_identifier="second-company",
                )
            ],
        },
        session_factory=session_factory,
    )

    result = pipeline.run([
        first_source,
        second_source,
    ])

    assert result.collected_jobs == 2
    assert result.successful_collections == 2
    assert result.new_jobs == 2
    assert result.updated_jobs == 0
    assert count_records(session_factory) == 2

def test_reports_jobs_removed_between_runs(
    database: tuple[
        Engine,
        sessionmaker[Session],
    ],
) -> None:
    _, session_factory = database
    source = create_company_source()

    postings = {
        "example-company": [
            create_raw_posting(
                external_id="current"
            ),
            create_raw_posting(
                external_id="removed"
            ),
        ]
    }

    pipeline = create_pipeline(
        postings=postings,
        session_factory=session_factory,
    )

    first_result = pipeline.run([source])

    postings["example-company"] = [
        create_raw_posting(
            external_id="current"
        )
    ]

    second_result = pipeline.run([source])

    with session_factory() as session:
        removed_record = session.scalar(
            select(JobRecord).where(
                JobRecord.company == "Example Company",
                JobRecord.requisition_id == "removed",
            )
        )

    assert first_result.deactivated_jobs == 0
    assert second_result.deactivated_jobs == 1
    assert removed_record is not None
    assert removed_record.is_active is False