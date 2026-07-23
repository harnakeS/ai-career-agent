from collections.abc import Iterator
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import (
    Base,
    JobRecord,
)
from app.models.job import JobPosting
from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.cache_service import (
    CachedRequirementsExtractionService,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
)


class CountingRequirementsExtractor:
    """Deterministic extractor that records invocation count."""

    def __init__(self) -> None:
        self.call_count = 0

    def extract(
        self,
        job: JobPosting,
    ) -> ExtractedJobRequirements:
        self.call_count += 1

        return ExtractedJobRequirements(
            requirements=[
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=(
                        RequirementImportance.REQUIRED
                    ),
                    value="SQL",
                    source_text="SQL is required.",
                )
            ]
        )


@pytest.fixture
def session_factory(
) -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite:///:memory:"
    )
    Base.metadata.create_all(engine)

    factory = sessionmaker(bind=engine)

    yield factory

    engine.dispose()


def create_job(
    *,
    description: str = "SQL is required.",
    requisition_id: str = "REQ-123",
) -> JobPosting:
    return JobPosting(
        company="Example Company",
        requisition_id=requisition_id,
        title="Data Analyst",
        location="New York, NY",
        description=description,
        application_url=(
            f"https://example.com/jobs/{requisition_id}"
        ),
    )


def persist_job(
    factory: sessionmaker[Session],
    job: JobPosting,
) -> None:
    current_time = datetime.now(timezone.utc)

    with factory() as session:
        session.add(
            JobRecord(
                company=job.company,
                requisition_id=job.requisition_id,
                title=job.title,
                location=job.location,
                description=job.description,
                application_url=str(
                    job.application_url
                ),
                date_discovered=current_time,
                last_seen=current_time,
                is_active=True,
                alert_sent=False,
            )
        )
        session.commit()


def create_cached_service(
    factory: sessionmaker[Session],
    extractor: CountingRequirementsExtractor,
    *,
    model_name: str = "qwen3.5:4b",
) -> CachedRequirementsExtractionService:
    delegate = RequirementsExtractionService(
        extractor=extractor
    )

    return CachedRequirementsExtractionService(
        delegate=delegate,
        session_factory=factory,
        provider="ollama",
        model_name=model_name,
        extractor_version="1",
    )


def test_repeated_extraction_invokes_ai_once(
    session_factory: sessionmaker[Session],
) -> None:
    job = create_job()
    persist_job(session_factory, job)

    extractor = CountingRequirementsExtractor()
    service = create_cached_service(
        session_factory,
        extractor,
    )

    first_result = service.extract_with_metadata(job)
    second_result = service.extract_with_metadata(job)

    assert (
        first_result.requirements
        == second_result.requirements
    )
    assert first_result.cache_hit is False
    assert second_result.cache_hit is True
    assert extractor.call_count == 1


def test_changed_description_invokes_ai_again(
    session_factory: sessionmaker[Session],
) -> None:
    original_job = create_job()
    persist_job(session_factory, original_job)

    extractor = CountingRequirementsExtractor()
    service = create_cached_service(
        session_factory,
        extractor,
    )

    service.extract(original_job)

    changed_job = create_job(
        description=(
            "SQL and Python are now required."
        )
    )

    service.extract(changed_job)

    assert extractor.call_count == 2


def test_unstored_job_is_not_cached(
    session_factory: sessionmaker[Session],
) -> None:
    job = create_job(
        requisition_id="NOT-STORED"
    )

    extractor = CountingRequirementsExtractor()
    service = create_cached_service(
        session_factory,
        extractor,
    )

    service.extract(job)
    service.extract(job)

    assert extractor.call_count == 2