from collections.abc import Callable

from sqlalchemy.orm import Session

from app.database.repository import JobRepository
from app.database.requirements_cache_repository import (
    JobRequirementsCacheRepository,
)
from app.models.job import JobPosting
from app.models.job_requirements import (
    JobRequirements,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
    RequirementsExtractionResult,

)


class CachedRequirementsExtractionService(
    RequirementsExtractionService
):
    """
    Reuse persisted requirements before invoking the AI extractor.

    Jobs that are not stored in the local database are extracted
    normally but cannot be cached.
    """

    def __init__(
        self,
        *,
        delegate: RequirementsExtractionService,
        session_factory: Callable[[], Session],
        provider: str,
        model_name: str,
        extractor_version: str,
    ) -> None:
        self._delegate = delegate
        self._session_factory = session_factory
        self._provider = provider
        self._model_name = model_name
        self._extractor_version = extractor_version

    def extract(
        self,
        job: JobPosting,
    ) -> JobRequirements:
        return self.extract_with_metadata(
            job
        ).requirements

    def extract_with_metadata(
        self,
        job: JobPosting,
    ) -> RequirementsExtractionResult:
        """Return cached requirements or extract and persist them."""

        job_id = self._find_job_id(job)

        if job_id is not None:
            cached = self._load_cached_requirements(
                job_id=job_id,
                job=job,
            )

            if cached is not None:
                return RequirementsExtractionResult(
                    requirements=cached,
                    cache_hit=True,
                )

        requirements = self._delegate.extract(job)

        if job_id is not None:
            self._save_requirements(
                job_id=job_id,
                job=job,
                requirements=requirements,
            )

        return RequirementsExtractionResult(
            requirements=requirements,
            cache_hit=False,
        )

    def _find_job_id(
        self,
        job: JobPosting,
    ) -> int | None:
        with self._session_factory() as session:
            repository = JobRepository(session)

            record = repository.get_by_requisition(
                company=job.company,
                requisition_id=job.requisition_id,
            )

            if record is None:
                return None

            return record.id

    def _load_cached_requirements(
        self,
        *,
        job_id: int,
        job: JobPosting,
    ) -> JobRequirements | None:
        with self._session_factory() as session:
            repository = (
                JobRequirementsCacheRepository(session)
            )

            return repository.get(
                job_id=job_id,
                description=job.description,
                provider=self._provider,
                model_name=self._model_name,
                extractor_version=self._extractor_version,
            )

    def _save_requirements(
        self,
        *,
        job_id: int,
        job: JobPosting,
        requirements: JobRequirements,
    ) -> None:
        with self._session_factory() as session:
            repository = (
                JobRequirementsCacheRepository(session)
            )

            try:
                repository.save(
                    job_id=job_id,
                    description=job.description,
                    provider=self._provider,
                    model_name=self._model_name,
                    extractor_version=self._extractor_version,
                    requirements=requirements,
                )
                session.commit()

            except Exception:
                session.rollback()
                raise