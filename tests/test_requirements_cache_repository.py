from datetime import datetime, timezone
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import (
    Base,
    JobRecord,
    JobRequirementsCacheRecord,
)
from app.database.requirements_cache_repository import (
    JobRequirementsCacheRepository,
)
from app.models.job_requirements import (
    JobRequirements,
    Requirement,
    RequirementCategory,
    RequirementImportance,
)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite:///:memory:"
    )
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    database_session = session_factory()

    try:
        yield database_session
    finally:
        database_session.close()


def create_job_record(
    session: Session,
) -> JobRecord:
    current_time = datetime.now(timezone.utc)

    record = JobRecord(
        company="Example Company",
        requisition_id="REQ-123",
        title="Data Analyst",
        location="New York, NY",
        description="SQL or Python experience is required.",
        application_url=(
            "https://example.com/jobs/REQ-123"
        ),
        date_discovered=current_time,
        last_seen=current_time,
        is_active=True,
        alert_sent=False,
    )

    session.add(record)
    session.flush()

    return record


def create_requirements() -> JobRequirements:
    return JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="SQL",
                alternatives=["Python"],
                source_text=(
                    "SQL or Python experience is required."
                ),
            )
        ],
        entry_level=True,
    )


def test_saves_and_retrieves_requirements(
    session: Session,
) -> None:
    job = create_job_record(session)
    repository = JobRequirementsCacheRepository(
        session
    )
    requirements = create_requirements()

    repository.save(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
        requirements=requirements,
    )
    session.commit()

    result = repository.get(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
    )

    assert result == requirements
    assert result.requirements[0].alternatives == [
        "Python"
    ]


def test_changed_description_invalidates_cache(
    session: Session,
) -> None:
    job = create_job_record(session)
    repository = JobRequirementsCacheRepository(
        session
    )

    repository.save(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
        requirements=create_requirements(),
    )
    session.commit()

    result = repository.get(
        job_id=job.id,
        description="The posting has changed.",
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
    )

    assert result is None


def test_save_replaces_stale_description_result(
    session: Session,
) -> None:
    job = create_job_record(session)
    repository = JobRequirementsCacheRepository(
        session
    )

    repository.save(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
        requirements=create_requirements(),
    )

    updated_requirements = JobRequirements(
        requirements=[
            Requirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Java",
                source_text="Java is required.",
            )
        ]
    )

    repository.save(
        job_id=job.id,
        description="Java is required.",
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
        requirements=updated_requirements,
    )
    session.commit()

    records = list(
        session.scalars(
            select(JobRequirementsCacheRecord)
        ).all()
    )

    result = repository.get(
        job_id=job.id,
        description="Java is required.",
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
    )

    assert len(records) == 1
    assert result == updated_requirements


def test_does_not_reuse_different_model_or_version(
    session: Session,
) -> None:
    job = create_job_record(session)
    repository = JobRequirementsCacheRepository(
        session
    )

    repository.save(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="1",
        requirements=create_requirements(),
    )
    session.commit()

    different_model = repository.get(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="different-model",
        extractor_version="1",
    )

    different_version = repository.get(
        job_id=job.id,
        description=job.description,
        provider="ollama",
        model_name="qwen3.5:4b",
        extractor_version="2",
    )

    assert different_model is None
    assert different_version is None