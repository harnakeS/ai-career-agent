from collections.abc import Callable, Iterable

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.job_sources.collection import (
    CompanyCollectionResult,
    CompanyJobCollectionService,
)
from app.job_sources.models import CompanySource
from app.pipeline.company_persistence import (
    CompanyJobPersistenceService,
    CompanyPersistenceResult,
)


SessionFactory = Callable[[], Session]


class SelectedCompanyRunResult(BaseModel):
    """Complete result of one selected-company pipeline run."""

    collection: CompanyCollectionResult
    persistence: CompanyPersistenceResult

    @property
    def collected_jobs(self) -> int:
        return len(self.collection.jobs)

    @property
    def new_jobs(self) -> int:
        return self.persistence.new_jobs

    @property
    def updated_jobs(self) -> int:
        return self.persistence.updated_jobs

    @property
    def successful_collections(self) -> int:
        return len(self.collection.snapshots)

    @property
    def skipped_sources(self) -> int:
        return len(self.collection.skipped_sources)

    @property
    def collection_failures(self) -> int:
        return len(self.collection.failures)

    @property
    def persistence_failures(self) -> int:
        return len(self.persistence.failures)


class SelectedCompanyPipeline:
    """Coordinate selected-company collection and persistence."""

    def __init__(
        self,
        collection_service: CompanyJobCollectionService,
        session_factory: SessionFactory,
    ) -> None:
        self._collection_service = collection_service
        self._session_factory = session_factory

    def run(
        self,
        sources: Iterable[CompanySource],
    ) -> SelectedCompanyRunResult:
        collection_result = (
            self._collection_service.collect(sources)
        )

        with self._session_factory() as session:
            persistence_service = (
                CompanyJobPersistenceService(
                    session=session
                )
            )
            persistence_result = (
                persistence_service.persist(
                    collection_result
                )
            )

        return SelectedCompanyRunResult(
            collection=collection_result,
            persistence=persistence_result,
        )