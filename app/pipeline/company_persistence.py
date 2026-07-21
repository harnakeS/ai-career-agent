from collections.abc import Callable

from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.repository import JobRepository
from app.job_sources.collection import (
    CompanyCollectionResult,
)
from app.job_sources.models import CompanySource


RepositoryFactory = Callable[
    [Session],
    JobRepository,
]


class CompanyPersistenceSummary(BaseModel):
    """Persistence counts for one successful company snapshot."""

    source: CompanySource
    new_jobs: int = Field(ge=0)
    updated_jobs: int = Field(ge=0)
    deactivated_jobs: int = Field(ge=0)


class CompanyPersistenceFailure(BaseModel):
    """Database failure encountered for one company snapshot."""

    source: CompanySource
    error_type: str
    message: str


class CompanyPersistenceResult(BaseModel):
    """Combined result of persisting company snapshots."""

    summaries: list[CompanyPersistenceSummary] = Field(
        default_factory=list
    )
    failures: list[CompanyPersistenceFailure] = Field(
        default_factory=list
    )

    @property
    def new_jobs(self) -> int:
        """Return the total number of inserted jobs."""

        return sum(
            summary.new_jobs
            for summary in self.summaries
        )

    @property
    def updated_jobs(self) -> int:
        """Return the total number of updated jobs."""

        return sum(
            summary.updated_jobs
            for summary in self.summaries
        )

    @property
    def deactivated_jobs(self) -> int:
        """Return the total number of deactivated jobs."""

        return sum(
            summary.deactivated_jobs
            for summary in self.summaries
        )


class CompanyJobPersistenceService:
    """Persist each successful company snapshot transactionally."""

    def __init__(
        self,
        session: Session,
        repository_factory: RepositoryFactory = JobRepository,
    ) -> None:
        self._session = session
        self._repository_factory = repository_factory

    def persist(
        self,
        collection_result: CompanyCollectionResult,
    ) -> CompanyPersistenceResult:
        result = CompanyPersistenceResult()
        repository = self._repository_factory(
            self._session
        )

        for snapshot in collection_result.snapshots:
            new_jobs = 0
            updated_jobs = 0

            try:
                for job in snapshot.jobs:
                    _, created = repository.save_or_update(
                        job
                    )

                    if created:
                        new_jobs += 1
                    else:
                        updated_jobs += 1

                active_requisition_ids = {
                    job.requisition_id
                    for job in snapshot.jobs
                }

                deactivated_jobs = (
                    repository.deactivate_missing(
                        company=(
                            snapshot.source.company_name
                        ),
                        active_requisition_ids=(
                            active_requisition_ids
                        ),
                    )
                )

                self._session.commit()

            except SQLAlchemyError as exc:
                self._session.rollback()

                result.failures.append(
                    CompanyPersistenceFailure(
                        source=snapshot.source,
                        error_type=type(exc).__name__,
                        message=str(exc),
                    )
                )
                continue

            except Exception:
                self._session.rollback()
                raise

            result.summaries.append(
                CompanyPersistenceSummary(
                    source=snapshot.source,
                    new_jobs=new_jobs,
                    updated_jobs=updated_jobs,
                    deactivated_jobs=deactivated_jobs,
                )
            )

        return result