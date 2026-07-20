from datetime import date, datetime

from pydantic import ValidationError

from app.job_sources.errors import JobPostingConversionError
from app.job_sources.models import RawJobPosting
from app.models.job import JobPosting
from app.processing.job_description import (
    normalize_job_description,
)


class JobPostingConverter:
    """Convert provider-neutral raw postings into canonical job postings."""

    def convert(
        self,
        posting: RawJobPosting,
    ) -> JobPosting:
        description = normalize_job_description(
            posting.description
        )

        if not description:
            raise JobPostingConversionError(
                "Raw job posting must contain a nonblank description."
            )

        date_posted = self._parse_published_date(
            posting.published_at
        )

        try:
            return JobPosting(
                company=posting.company_name,
                requisition_id=posting.external_id,
                title=posting.title,
                location=posting.location,
                description=description,
                application_url=posting.application_url,
                date_posted=date_posted,
            )

        except ValidationError as exc:
            raise JobPostingConversionError(
                "Raw job posting could not be converted into "
                "a canonical job posting."
            ) from exc

    @staticmethod
    def _parse_published_date(
        value: str | None,
    ) -> date | None:
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        if normalized_value.endswith("Z"):
            normalized_value = (
                f"{normalized_value[:-1]}+00:00"
            )

        try:
            return datetime.fromisoformat(
                normalized_value
            ).date()

        except ValueError as exc:
            raise JobPostingConversionError(
                f"Invalid publication timestamp: '{value}'."
            ) from exc