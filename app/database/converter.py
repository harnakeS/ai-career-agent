from app.database.models import JobRecord
from app.models.job import JobPosting


def job_record_to_posting(
    record: JobRecord,
) -> JobPosting:
    """Convert a persisted job record into the canonical job model."""

    return JobPosting(
        company=record.company,
        requisition_id=record.requisition_id,
        title=record.title,
        location=record.location,
        description=record.description,
        application_url=record.application_url,
        date_posted=record.date_posted,
        date_discovered=record.date_discovered,
    )