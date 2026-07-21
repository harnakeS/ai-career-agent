import argparse
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from app.database.models import Base, JobRecord
from app.job_sources.collection import (
    CompanyJobCollectionService,
    CompanyCollectionResult,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)
from app.pipeline.company_persistence import (
    CompanyJobPersistenceService,
)
from app.job_sources.registry import JobSourceRegistry


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect and convert jobs from a public Greenhouse board."
        )
    )
    parser.add_argument(
        "board_token",
        help="Greenhouse board token from the company's job-board URL.",
    )
    parser.add_argument(
        "company_name",
        help="Company name stored on collected postings.",
    )
    parser.add_argument(
        "careers_url",
        help="Company's public careers-page URL.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    company_source = CompanySource(
        company_name=arguments.company_name,
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier=arguments.board_token,
        careers_url=arguments.careers_url,
    )

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

    result = collection_service.collect([
        company_source
    ])

    if result.failures:
        print("Collection failed.")

        for failure in result.failures:
            print()
            print(f"Company: {failure.company_name}")
            print(f"Provider: {failure.provider.value}")
            print(f"Error type: {failure.error_type}")
            print(f"Message: {failure.message}")

        raise SystemExit(1)

    print(
        f"Successful company sources: "
        f"{len(result.successful_sources)}"
    )
    print(
        f"Skipped company sources: "
        f"{len(result.skipped_sources)}"
    )
    print(
        f"Collected and converted "
        f"{len(result.jobs)} canonical posting(s) "
        f"for {company_source.company_name}."
    )

    postings_with_dates = sum(
        posting.date_posted is not None
        for posting in result.jobs
    )

    print(
        f"Postings with original publication dates: "
        f"{postings_with_dates}"
    )

    verify_temporary_persistence(result)

    for posting in result.jobs[:5]:
        print()
        print(f"ID: {posting.requisition_id}")
        print(f"Title: {posting.title}")
        print(
            f"Location: "
            f"{posting.location or 'Not specified'}"
        )
        print(
            f"Published: "
            f"{posting.date_posted or 'Not supplied'}"
        )
        print(
            f"Description length: "
            f"{len(posting.description)} characters"
        )
        print(f"Apply: {posting.application_url}")

def verify_temporary_persistence(
    collection_result: CompanyCollectionResult,
) -> None:
    """
    Persist the live collection twice in a temporary database.

    The first pass should insert every job. The second pass should
    update the same records without creating duplicates.
    """

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )
    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            persistence_service = (
                CompanyJobPersistenceService(
                    session=session
                )
            )

            first_result = persistence_service.persist(
                collection_result
            )

            if first_result.failures:
                failure = first_result.failures[0]

                raise SystemExit(
                    "First persistence pass failed for "
                    f"'{failure.source.company_name}': "
                    f"{failure.error_type}: "
                    f"{failure.message}"
                )

            second_result = persistence_service.persist(
                collection_result
            )

            if second_result.failures:
                failure = second_result.failures[0]

                raise SystemExit(
                    "Second persistence pass failed for "
                    f"'{failure.source.company_name}': "
                    f"{failure.error_type}: "
                    f"{failure.message}"
                )

            row_count = session.scalar(
                select(func.count()).select_from(
                    JobRecord
                )
            ) or 0

    finally:
        engine.dispose()

    expected_jobs = len(collection_result.jobs)

    print()
    print("Temporary Persistence Check")
    print("---------------------------")
    print(
        f"First pass new jobs: "
        f"{first_result.new_jobs}"
    )
    print(
        f"First pass updated jobs: "
        f"{first_result.updated_jobs}"
    )
    print(
        f"Second pass new jobs: "
        f"{second_result.new_jobs}"
    )
    print(
        f"Second pass updated jobs: "
        f"{second_result.updated_jobs}"
    )
    print(f"Final database rows: {row_count}")

    if (
        first_result.new_jobs != expected_jobs
        or first_result.updated_jobs != 0
        or second_result.new_jobs != 0
        or second_result.updated_jobs != expected_jobs
        or row_count != expected_jobs
    ):
        raise SystemExit(
            "Temporary persistence results did not match "
            "the expected insert-and-update behavior."
        )

    print("Duplicate prevention verified.")


if __name__ == "__main__":
    main()