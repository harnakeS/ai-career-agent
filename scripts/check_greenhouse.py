import argparse

from app.job_sources.converter import JobPostingConverter
from app.job_sources.errors import (
    JobPostingConversionError,
    JobSourceError,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting
)
from app.models.job import JobPosting


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


def convert_postings(
    raw_postings: list[RawJobPosting],
) -> list[JobPosting]:
    converter = JobPostingConverter()
    converted_postings: list[JobPosting] = []

    for raw_posting in raw_postings:
        try:
            converted_posting = converter.convert(
                raw_posting
            )
        except JobPostingConversionError as exc:
            raise SystemExit(
                "Unable to convert Greenhouse posting "
                f"'{raw_posting.external_id}' "
                f"('{raw_posting.title}'): {exc}"
            ) from exc

        converted_postings.append(converted_posting)

    return converted_postings


def main() -> None:
    arguments = parse_arguments()

    source = CompanySource(
        company_name=arguments.company_name,
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier=arguments.board_token,
        careers_url=arguments.careers_url,
    )

    collector = GreenhouseJobSource()

    try:
        raw_postings = collector.collect(source)
    except JobSourceError as exc:
        raise SystemExit(
            f"Greenhouse collection failed: {exc}"
        ) from exc

    postings = convert_postings(raw_postings)

    print(
        f"Collected {len(raw_postings)} raw posting(s) "
        f"for {source.company_name}."
    )
    print(
        f"Converted {len(postings)} canonical posting(s)."
    )

    postings_with_dates = sum(
        posting.date_posted is not None
        for posting in postings
    )

    print(
        f"Postings with original publication dates: "
        f"{postings_with_dates}"
    )

    for posting in postings[:5]:
        print()
        print(f"ID: {posting.requisition_id}")
        print(f"Title: {posting.title}")
        print(f"Location: {posting.location or 'Not specified'}")
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