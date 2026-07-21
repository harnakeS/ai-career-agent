from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Base, JobRecord
from app.database.repository import JobRepository
from app.job_sources.collection import (
    CompanyCollectionResult,
    CompanyJobSnapshot,
)
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)
from app.models.job import JobPosting
from app.pipeline.company_persistence import (
    CompanyJobPersistenceService,
)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )
    Base.metadata.create_all(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


def create_company_source(
    *,
    company_name: str = "Example Company",
    source_identifier: str = "example-company",
) -> CompanySource:
    return CompanySource(
        company_name=company_name,
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier=source_identifier,
        careers_url="https://example.com/careers",
    )


def create_job(
    *,
    company_name: str = "Example Company",
    requisition_id: str = "12345",
    title: str = "Software Engineer",
) -> JobPosting:
    return JobPosting(
        company=company_name,
        requisition_id=requisition_id,
        title=title,
        location="New York, NY",
        description="Build and maintain software systems.",
        application_url=(
            f"https://example.com/jobs/{requisition_id}"
        ),
    )


def create_collection_result(
    *,
    source: CompanySource | None = None,
    jobs: list[JobPosting] | None = None,
) -> CompanyCollectionResult:
    company_source = source or create_company_source()

    return CompanyCollectionResult(
        snapshots=[
            CompanyJobSnapshot(
                source=company_source,
                jobs=jobs or [],
            )
        ]
    )


def count_records(
    session: Session,
) -> int:
    return session.scalar(
        select(func.count()).select_from(JobRecord)
    ) or 0


def test_persists_new_company_jobs(
    session: Session,
) -> None:
    service = CompanyJobPersistenceService(session)
    collection_result = create_collection_result(
        jobs=[
            create_job(requisition_id="111"),
            create_job(requisition_id="222"),
        ]
    )

    result = service.persist(collection_result)

    assert result.new_jobs == 2
    assert result.updated_jobs == 0
    assert len(result.summaries) == 1
    assert result.failures == []
    assert count_records(session) == 2


def test_repeated_snapshot_updates_without_duplicates(
    session: Session,
) -> None:
    service = CompanyJobPersistenceService(session)

    first_result = service.persist(
        create_collection_result(
            jobs=[
                create_job(
                    title="Original Software Engineer"
                )
            ]
        )
    )
    second_result = service.persist(
        create_collection_result(
            jobs=[
                create_job(
                    title="Updated Software Engineer"
                )
            ]
        )
    )

    record = session.scalar(
        select(JobRecord).where(
            JobRecord.company == "Example Company",
            JobRecord.requisition_id == "12345",
        )
    )

    assert first_result.new_jobs == 1
    assert second_result.new_jobs == 0
    assert second_result.updated_jobs == 1
    assert count_records(session) == 1
    assert record is not None
    assert record.title == "Updated Software Engineer"


def test_empty_company_snapshot_is_successful(
    session: Session,
) -> None:
    source = create_company_source()
    service = CompanyJobPersistenceService(session)

    result = service.persist(
        create_collection_result(
            source=source,
            jobs=[],
        )
    )

    assert len(result.summaries) == 1
    assert result.summaries[0].source == source
    assert result.summaries[0].new_jobs == 0
    assert result.summaries[0].updated_jobs == 0
    assert result.failures == []


def test_database_failure_rolls_back_only_failing_company(
    session: Session,
) -> None:
    class SelectiveFailureRepository(JobRepository):
        def save_or_update(
            self,
            job: JobPosting,
        ) -> tuple[JobRecord, bool]:
            if job.requisition_id == "fail":
                raise SQLAlchemyError(
                    "Simulated database failure."
                )

            return super().save_or_update(job)

    successful_source = create_company_source(
        company_name="Successful Company",
        source_identifier="successful-company",
    )
    failing_source = create_company_source(
        company_name="Failing Company",
        source_identifier="failing-company",
    )

    collection_result = CompanyCollectionResult(
        snapshots=[
            CompanyJobSnapshot(
                source=successful_source,
                jobs=[
                    create_job(
                        company_name="Successful Company",
                        requisition_id="success",
                    )
                ],
            ),
            CompanyJobSnapshot(
                source=failing_source,
                jobs=[
                    create_job(
                        company_name="Failing Company",
                        requisition_id="partial",
                    ),
                    create_job(
                        company_name="Failing Company",
                        requisition_id="fail",
                    ),
                ],
            ),
        ]
    )

    service = CompanyJobPersistenceService(
        session=session,
        repository_factory=SelectiveFailureRepository,
    )

    result = service.persist(collection_result)

    stored_records = session.scalars(
        select(JobRecord)
    ).all()

    assert len(result.summaries) == 1
    assert (
        result.summaries[0].source
        == successful_source
    )
    assert len(result.failures) == 1
    assert result.failures[0].source == failing_source
    assert result.failures[0].error_type == "SQLAlchemyError"

    assert len(stored_records) == 1
    assert (
        stored_records[0].company
        == "Successful Company"
    )


def test_unexpected_error_rolls_back_and_propagates(
    session: Session,
) -> None:
    class BrokenRepository(JobRepository):
        def save_or_update(
            self,
            job: JobPosting,
        ) -> tuple[JobRecord, bool]:
            if job.requisition_id == "broken":
                raise RuntimeError(
                    "Unexpected persistence bug."
                )

            return super().save_or_update(job)

    collection_result = create_collection_result(
        jobs=[
            create_job(requisition_id="partial"),
            create_job(requisition_id="broken"),
        ]
    )
    service = CompanyJobPersistenceService(
        session=session,
        repository_factory=BrokenRepository,
    )

    with pytest.raises(
        RuntimeError,
        match="Unexpected persistence bug",
    ):
        service.persist(collection_result)

    assert count_records(session) == 0


def test_collection_without_snapshots_changes_nothing(
    session: Session,
) -> None:
    service = CompanyJobPersistenceService(session)

    result = service.persist(
        CompanyCollectionResult()
    )

    assert result.summaries == []
    assert result.failures == []
    assert result.new_jobs == 0
    assert result.updated_jobs == 0
    assert count_records(session) == 0