from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import JobRecord
from app.models.job import JobPosting


class JobRepository:
    """Handles database operations for job postings."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_requisition(
        self,
        company: str,
        requisition_id: str,
    ) -> JobRecord | None:
        statement = select(JobRecord).where(
            JobRecord.company == company,
            JobRecord.requisition_id == requisition_id,
        )

        return self.session.scalar(statement)

    def save_or_update(self, job: JobPosting) -> tuple[JobRecord, bool]:
        """
        Insert a new job or update an existing job.

        Returns:
            A tuple containing:
            - the saved database record
            - True if the job was newly inserted, otherwise False
        """
        existing_job = self.get_by_requisition(
            company=job.company,
            requisition_id=job.requisition_id,
        )

        current_time = datetime.now(timezone.utc)

        if existing_job is not None:
            existing_job.title = job.title
            existing_job.location = job.location
            existing_job.description = job.description
            existing_job.application_url = str(job.application_url)
            existing_job.date_posted = job.date_posted
            existing_job.last_seen = current_time
            existing_job.is_active = True

            self.session.commit()
            self.session.refresh(existing_job)

            return existing_job, False

        new_job = JobRecord(
            company=job.company,
            requisition_id=job.requisition_id,
            title=job.title,
            location=job.location,
            description=job.description,
            application_url=str(job.application_url),
            date_posted=job.date_posted,
            date_discovered=job.date_discovered,
            last_seen=current_time,
            is_active=True,
            alert_sent=False,
        )

        self.session.add(new_job)
        self.session.commit()
        self.session.refresh(new_job)

        return new_job, True