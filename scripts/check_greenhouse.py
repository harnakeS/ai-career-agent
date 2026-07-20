import argparse

from app.job_sources.errors import JobSourceError
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check a public Greenhouse job board."
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

    source = CompanySource(
        company_name=arguments.company_name,
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier=arguments.board_token,
        careers_url=arguments.careers_url,
    )

    collector = GreenhouseJobSource()

    try:
        postings = collector.collect(source)
    except JobSourceError as exc:
        raise SystemExit(
            f"Greenhouse collection failed: {exc}"
        ) from exc

    print(
        f"Collected {len(postings)} active posting(s) "
        f"for {source.company_name}."
    )

    for posting in postings[:5]:
        print()
        print(f"ID: {posting.external_id}")
        print(f"Title: {posting.title}")
        print(f"Location: {posting.location or 'Not specified'}")
        print(f"Updated: {posting.posted_at or 'Not specified'}")
        print(f"Apply: {posting.application_url}")


if __name__ == "__main__":
    main()