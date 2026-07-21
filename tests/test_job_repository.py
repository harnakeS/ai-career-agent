from collections.abc import Iterator
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.models import Base, JobRecord
from app.database.repository import JobRepository
from app.models.job import JobPosting


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )
    Base.metadata.create_all(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


def create_job(
    *,
    title: str = "Software Engineer",
    description: str = "Build software systems.",
    location: str | None = "New York, NY",
    date_discovered: datetime | None = None,
) -> JobPosting:
    return JobPosting(
        company="Example Company",
        requisition_id="12345",
        title=title,
        location=location,
        description=description,
        application_url="https://example.com/jobs/12345",
        date_posted=date(2026, 7, 20),
        date_discovered=(
            date_discovered
            or datetime.now(timezone.utc)
        ),
    )


def test_inserts_new_job(
    session: Session,
) -> None:
    repository = JobRepository(session)

    record, created = repository.save_or_update(
        create_job()
    )

    assert created is True
    assert record.id is not None
    assert record.company == "Example Company"
    assert record.requisition_id == "12345"
    assert record.is_active is True


def test_updates_existing_job_without_duplicate(
    session: Session,
) -> None:
    repository = JobRepository(session)

    original_record, _ = repository.save_or_update(
        create_job()
    )
    session.commit()

    updated_record, created = repository.save_or_update(
        create_job(
            title="Updated Software Engineer",
            description="Build updated software systems.",
        )
    )

    record_count = session.scalar(
        select(func.count()).select_from(JobRecord)
    )

    assert created is False
    assert updated_record.id == original_record.id
    assert updated_record.title == (
        "Updated Software Engineer"
    )
    assert updated_record.description == (
        "Build updated software systems."
    )
    assert record_count == 1


def test_update_reactivates_existing_job(
    session: Session,
) -> None:
    repository = JobRepository(session)

    record, _ = repository.save_or_update(
        create_job()
    )
    session.commit()

    record.is_active = False
    session.commit()

    updated_record, created = repository.save_or_update(
        create_job()
    )

    assert created is False
    assert updated_record.is_active is True


def test_update_preserves_original_discovery_time(
    session: Session,
) -> None:
    repository = JobRepository(session)

    original_record, _ = repository.save_or_update(
        create_job(
            date_discovered=datetime(
                2026,
                7,
                18,
                12,
                0,
                tzinfo=timezone.utc,
            )
        )
    )
    session.commit()

    persisted_discovery_time = (
        original_record.date_discovered
    )

    repository.save_or_update(
        create_job(
            date_discovered=datetime(
                2026,
                7,
                20,
                12,
                0,
                tzinfo=timezone.utc,
            )
        )
    )

    assert (
        original_record.date_discovered
        == persisted_discovery_time
    )


def test_caller_can_roll_back_uncommitted_insert(
    session: Session,
) -> None:
    repository = JobRepository(session)

    repository.save_or_update(create_job())
    session.rollback()

    result = repository.get_by_requisition(
        company="Example Company",
        requisition_id="12345",
    )

    assert result is None