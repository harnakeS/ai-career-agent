from datetime import date, datetime, timezone

from app.dashboard.view_models import (
    company_source_to_row,
    filter_job_rows,
    job_record_to_row,
    job_record_to_detail,
)
from app.database.models import JobRecord
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
)


def create_job_record(
    *,
    company: str = "Example Company",
    title: str = "Software Engineer",
    location: str | None = "New York, NY",
    is_active: bool = True,
    match_score: float | None = None,
    application_status: str | None = None,
) -> JobRecord:
    return JobRecord(
        id=1,
        company=company,
        requisition_id="12345",
        title=title,
        location=location,
        description="Build software systems.",
        application_url=(
            "https://example.com/jobs/12345"
        ),
        date_posted=date(2026, 7, 20),
        date_discovered=datetime(
            2026,
            7,
            20,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        last_seen=datetime(
            2026,
            7,
            21,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        is_active=is_active,
        alert_sent=False,
        match_score=match_score,
        application_status=application_status,
    )


def test_converts_active_job_record_to_table_row() -> None:
    row = job_record_to_row(
        create_job_record(
            match_score=87.5,
            application_status="Saved", 
        )
    )

    assert row == {
        "Company": "Example Company",
        "Title": "Software Engineer",
        "Job ID": 1,
        "Location": "New York, NY",
        "Posted": "2026-07-20",
        "Discovered": "2026-07-20",
        "Status": "Active",
        "Match Score": 87.5,
        "Application Status": "Saved",
        "Apply": "https://example.com/jobs/12345",
    }


def test_converts_missing_optional_job_values() -> None:
    row = job_record_to_row(
        create_job_record(
            location=None,
            is_active=False,
        )
    )

    assert row["Location"] == "Not specified"
    assert row["Status"] == "Inactive"
    assert row["Match Score"] is None
    assert row["Application Status"] == "Not applied"


def test_converts_company_source_to_table_row() -> None:
    source = CompanySource(
        company_name="Example Company",
        provider=JobSourceProvider.GREENHOUSE,
        source_identifier="example-company",
        careers_url="https://example.com/careers",
        enabled=True,
    )

    row = company_source_to_row(source)

    assert row == {
        "Company": "Example Company",
        "Provider": "Greenhouse",
        "Status": "Enabled",
        "Careers": "https://example.com/careers",
    }


def test_filters_jobs_by_company_and_search_query() -> None:
    rows = [
        job_record_to_row(
            create_job_record(
                company="First Company",
                title="Software Engineer",
                location="New York, NY",
            )
        ),
        job_record_to_row(
            create_job_record(
                company="Second Company",
                title="Data Analyst",
                location="Chicago, IL",
            )
        ),
    ]

    result = filter_job_rows(
        rows,
        query="software",
        companies={"First Company"},
    )

    assert len(result) == 1
    assert result[0]["Company"] == "First Company"
    assert result[0]["Title"] == "Software Engineer"


def test_empty_filters_return_all_jobs() -> None:
    rows = [
        job_record_to_row(
            create_job_record(
                company="First Company"
            )
        ),
        job_record_to_row(
            create_job_record(
                company="Second Company"
            )
        ),
    ]

    result = filter_job_rows(rows)

    assert result == rows

def test_converts_job_record_to_detail() -> None:
    detail = job_record_to_detail(
        create_job_record(
            match_score=87.5,
            application_status="Saved",
        )
    )

    assert detail == {
        "Job ID": 1,
        "Company": "Example Company",
        "Requisition ID": "12345",
        "Title": "Software Engineer",
        "Location": "New York, NY",
        "Description": "Build software systems.",
        "Posted": "2026-07-20",
        "Discovered": "2026-07-20",
        "Last Seen": "2026-07-21",
        "Status": "Active",
        "Match Score": 87.5,
        "Application Status": "Saved",
        "Application URL": (
            "https://example.com/jobs/12345"
        ),
    }