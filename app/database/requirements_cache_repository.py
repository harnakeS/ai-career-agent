from datetime import datetime, timezone
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    JobRequirementsCacheRecord,
)
from app.models.job_requirements import (
    JobRequirements,
)


class JobRequirementsCacheRepository:
    """Persist and retrieve AI-extracted job requirements."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get(
        self,
        *,
        job_id: int,
        description: str,
        provider: str,
        model_name: str,
        extractor_version: str,
    ) -> JobRequirements | None:
        """
        Return cached requirements when the complete cache identity
        and job-description digest still match.
        """

        record = self._get_record(
            job_id=job_id,
            provider=provider,
            model_name=model_name,
            extractor_version=extractor_version,
        )

        if record is None:
            return None

        current_digest = self._create_description_digest(
            description
        )

        if record.description_digest != current_digest:
            return None

        return JobRequirements.model_validate_json(
            record.requirements_json
        )

    def save(
        self,
        *,
        job_id: int,
        description: str,
        provider: str,
        model_name: str,
        extractor_version: str,
        requirements: JobRequirements,
    ) -> JobRequirementsCacheRecord:
        """
        Insert or update cached requirements.

        The caller owns the transaction and must commit or roll back.
        """

        record = self._get_record(
            job_id=job_id,
            provider=provider,
            model_name=model_name,
            extractor_version=extractor_version,
        )

        current_time = datetime.now(timezone.utc)
        description_digest = (
            self._create_description_digest(description)
        )
        requirements_json = (
            requirements.model_dump_json()
        )

        if record is not None:
            record.description_digest = description_digest
            record.requirements_json = requirements_json
            record.updated_at = current_time

            self.session.flush()

            return record

        record = JobRequirementsCacheRecord(
            job_id=job_id,
            provider=provider,
            model_name=model_name,
            extractor_version=extractor_version,
            description_digest=description_digest,
            requirements_json=requirements_json,
            created_at=current_time,
            updated_at=current_time,
        )

        self.session.add(record)
        self.session.flush()

        return record

    def _get_record(
        self,
        *,
        job_id: int,
        provider: str,
        model_name: str,
        extractor_version: str,
    ) -> JobRequirementsCacheRecord | None:
        statement = select(
            JobRequirementsCacheRecord
        ).where(
            JobRequirementsCacheRecord.job_id == job_id,
            JobRequirementsCacheRecord.provider == provider,
            JobRequirementsCacheRecord.model_name == model_name,
            (
                JobRequirementsCacheRecord.extractor_version
                == extractor_version
            ),
        )

        return self.session.scalar(statement)

    def _create_description_digest(
        self,
        description: str,
    ) -> str:
        return sha256(
            description.encode("utf-8")
        ).hexdigest()