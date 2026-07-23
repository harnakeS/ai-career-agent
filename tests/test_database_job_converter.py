from datetime import date, datetime, timezone

from app.database.converter import (
    job_record_to_posting,
)
from app.database.models import JobRecord


def test_converts_job_record_to_canonical_posting() -> None:
    record = JobRecord(
        id=1,
        company="Example Company",
        requisition_id="REQ-123",
        title="Software Engineer",
        location="New York, NY",
        description="Python and SQL are required.",
        application_url=(
            "https://example.com/jobs/REQ-123"
        ),
        date_posted=date(2026, 7, 20),
        date_discovered=datetime(
            2026,
            7,
            21,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        last_seen=datetime(
            2026,
            7,
            21,
            13,
            0,
            tzinfo=timezone.utc,
        ),
        is_active=True,
        alert_sent=False,
    )

    result = job_record_to_posting(record)

    assert result.company == "Example Company"
    assert result.requisition_id == "REQ-123"
    assert result.title == "Software Engineer"
    assert result.location == "New York, NY"
    assert result.description == (
        "Python and SQL are required."
    )
    assert str(result.application_url) == (
        "https://example.com/jobs/REQ-123"
    )
    assert result.date_posted == date(
        2026,
        7,
        20,
    )
    assert result.date_discovered == datetime(
        2026,
        7,
        21,
        12,
        0,
        tzinfo=timezone.utc,
    )