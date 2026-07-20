import argparse

from app.job_sources.collection import (
    CompanyJobCollectionService,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
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


if __name__ == "__main__":
    main()