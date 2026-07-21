from app.database.database import SessionLocal
from app.job_sources.collection import (
    CompanyJobCollectionService,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import JobSourceProvider
from app.job_sources.registry import JobSourceRegistry
from app.pipeline.selected_company_pipeline import (
    SelectedCompanyPipeline,
)


def create_selected_company_pipeline(
) -> SelectedCompanyPipeline:
    """
    Construct the selected-company pipeline with production dependencies.

    This composition function is shared by command-line and frontend
    entry points.
    """

    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: (
                GreenhouseJobSource()
            ),
        }
    )

    collection_service = CompanyJobCollectionService(
        registry=registry
    )

    return SelectedCompanyPipeline(
        collection_service=collection_service,
        session_factory=SessionLocal,
    )