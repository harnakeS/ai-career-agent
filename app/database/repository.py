from collections.abc import Collection
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database.models import JobRecord
from app.models.job import JobPosting


class JobRepository:
    """Handle database operations for job postings."""

    def __init__(
        self,
        session: Session,
    ) -> None:
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

    def list_jobs(
        self,
        *,
        active_only: bool = True,
    ) -> list[JobRecord]:
        """
        Return stored jobs ordered by discovery time.

        Inactive jobs are excluded by default because user-facing job
        discovery should prioritize currently available postings.
        """

        statement = select(JobRecord)

        if active_only:
            statement = statement.where(
                JobRecord.is_active.is_(True)
            )

        statement = statement.order_by(
            JobRecord.date_discovered.desc(),
            JobRecord.id.desc(),
        )

        return list(
            self.session.scalars(statement).all()
        )

    def deactivate_missing(
        self,
        *,
        company: str,
        active_requisition_ids: Collection[str],
    ) -> int:
        """
        Deactivate company jobs absent from a successful source snapshot.

        This method only prepares the changes. The caller owns the
        transaction and must commit or roll back the session.
        """

        statement = update(JobRecord).where(
            JobRecord.company == company,
            JobRecord.is_active.is_(True),
        )

        if active_requisition_ids:
            statement = statement.where(
                JobRecord.requisition_id.not_in(
                    active_requisition_ids
                )
            )

        result = self.session.execute(
            statement.values(is_active=False)
        )
        self.session.flush()

        return result.rowcount or 0

    def save_or_update(
        self,
        job: JobPosting,
    ) -> tuple[JobRecord, bool]:
        """
        Prepare an insert or update for a canonical job posting.

        Returns the affected database record and whether it was newly
        created. The caller owns the transaction and must commit or
        roll back the session.
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
            existing_job.application_url = str(
                job.application_url
            )
            existing_job.date_posted = job.date_posted
            existing_job.last_seen = current_time
            existing_job.is_active = True

            self.session.flush()

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
        self.session.flush()

        return new_job, True