from datetime import date

import pytest

from app.job_sources.converter import JobPostingConverter
from app.job_sources.errors import JobPostingConversionError
from app.job_sources.models import (
    JobSourceProvider,
    RawJobPosting,
)


def create_raw_posting(
    *,
    description: str = "Build and maintain software systems.",
    published_at: str | None = None,
    updated_at: str | None = None,
) -> RawJobPosting:
    return RawJobPosting(
        external_id="12345",
        company_name="Example Company",
        title="Software Engineer",
        location="New York, NY",
        description=description,
        application_url="https://example.com/jobs/12345",
        published_at=published_at,
        updated_at=updated_at,
        source_provider=JobSourceProvider.GREENHOUSE,
        source_identifier="example-company",
    )


def test_converts_raw_posting_to_canonical_job() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting()
    )

    assert result.company == "Example Company"
    assert result.requisition_id == "12345"
    assert result.title == "Software Engineer"
    assert result.location == "New York, NY"
    assert (
        str(result.application_url)
        == "https://example.com/jobs/12345"
    )


def test_preserves_plain_text_description() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description="Build and maintain software systems."
        )
    )

    assert (
        result.description
        == "Build and maintain software systems."
    )


def test_removes_html_from_description() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<p>Build software systems.</p>"
                "<p>Work with Python and SQL.</p>"
            )
        )
    )

    assert result.description == (
        "Build software systems.\n\n"
        "Work with Python and SQL."
    )


def test_decodes_html_entities() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<p>Research &amp; Development</p>"
            )
        )
    )

    assert result.description == "Research & Development"


def test_decodes_nested_html_entities() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "&lt;p&gt;Build Python services.&lt;/p&gt;"
            )
        )
    )

    assert result.description == "Build Python services."


def test_converts_publication_timestamp_to_date() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            published_at="2026-07-18T12:30:00-04:00"
        )
    )

    assert result.date_posted == date(2026, 7, 18)


def test_greenhouse_update_timestamp_is_not_publication_date() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            published_at=None,
            updated_at="2026-07-20T12:30:00-04:00",
        )
    )

    assert result.date_posted is None


def test_allows_missing_publication_timestamp() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting()
    )

    assert result.date_posted is None


def test_rejects_invalid_publication_timestamp() -> None:
    with pytest.raises(
        JobPostingConversionError,
        match="Invalid publication timestamp",
    ):
        JobPostingConverter().convert(
            create_raw_posting(
                published_at="not-a-timestamp"
            )
        )


def test_rejects_blank_normalized_description() -> None:
    with pytest.raises(
        JobPostingConversionError,
        match="nonblank description",
    ):
        JobPostingConverter().convert(
            create_raw_posting(
                description="<p>   </p>"
            )
        )

def test_preserves_html_headings_and_paragraphs() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<h2>Qualifications</h2>"
                "<p>Experience building software systems.</p>"
            )
        )
    )

    assert result.description == (
        "### Qualifications\n\n"
        "Experience building software systems."
    )


def test_converts_unordered_lists_to_markdown() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<p>Required skills:</p>"
                "<ul>"
                "<li>Python</li>"
                "<li>SQL</li>"
                "<li>Linux</li>"
                "</ul>"
            )
        )
    )

    assert result.description == (
        "Required skills:\n\n"
        "- Python\n"
        "- SQL\n"
        "- Linux"
    )


def test_converts_ordered_lists_to_markdown() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<ol>"
                "<li>Submit an application</li>"
                "<li>Complete the assessment</li>"
                "</ol>"
            )
        )
    )

    assert result.description == (
        "1. Submit an application\n"
        "2. Complete the assessment"
    )


def test_preserves_emphasis_and_safe_links() -> None:
    result = JobPostingConverter().convert(
        create_raw_posting(
            description=(
                "<p><strong>Important:</strong> "
                "Review the "
                "<a href=\"https://example.com/benefits\">"
                "benefits package"
                "</a>.</p>"
            )
        )
    )

    assert result.description == (
        "**Important:** Review the "
        "[benefits package]"
        "(https://example.com/benefits)."
    )