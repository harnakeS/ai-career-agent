from typing import Any
from urllib.parse import quote

from pydantic import ValidationError

from app.job_sources.errors import (
    InvalidJobSourceError,
    JobSourcePayloadError,
)
from app.job_sources.http import (
    JsonHttpClient,
    UrllibJsonHttpClient,
)
from app.job_sources.models import (
    CompanySource,
    JobSourceProvider,
    RawJobPosting,
)


class GreenhouseJobSource:
    """Collect published jobs from the Greenhouse Job Board API."""

    _JOBS_URL_TEMPLATE = (
        "https://boards-api.greenhouse.io/v1/boards/"
        "{board_token}/jobs?content=true"
    )

    def __init__(
        self,
        http_client: JsonHttpClient | None = None,
    ) -> None:
        self._http_client = http_client or UrllibJsonHttpClient()

    def collect(
        self,
        source: CompanySource,
    ) -> list[RawJobPosting]:
        if not source.enabled:
            return []

        if source.provider != JobSourceProvider.GREENHOUSE:
            raise InvalidJobSourceError(
                "GreenhouseJobSource requires a source configured "
                "with the greenhouse provider."
            )

        url = self._build_jobs_url(source.source_identifier)
        payload = self._http_client.get_json(url)

        jobs = payload.get("jobs")

        if not isinstance(jobs, list):
            raise JobSourcePayloadError(
                "Greenhouse response must contain a 'jobs' list."
            )

        return [
            self._convert_job(
                job=job,
                source=source,
            )
            for job in jobs
        ]

    def _build_jobs_url(
        self,
        board_token: str,
    ) -> str:
        encoded_token = quote(
            board_token,
            safe="",
        )

        return self._JOBS_URL_TEMPLATE.format(
            board_token=encoded_token,
        )

    def _convert_job(
        self,
        job: Any,
        source: CompanySource,
    ) -> RawJobPosting:
        if not isinstance(job, dict):
            raise JobSourcePayloadError(
                "Each Greenhouse job must be a JSON object."
            )

        external_id = job.get("id")
        title = job.get("title")
        application_url = job.get("absolute_url")
        description = job.get("content", "")
        posted_at = job.get("updated_at")
        location = self._extract_location(job)

        if external_id is None:
            raise JobSourcePayloadError(
                "Greenhouse job is missing its 'id'."
            )

        if not isinstance(title, str) or not title.strip():
            raise JobSourcePayloadError(
                "Greenhouse job is missing a valid 'title'."
            )

        if (
            not isinstance(application_url, str)
            or not application_url.strip()
        ):
            raise JobSourcePayloadError(
                "Greenhouse job is missing a valid 'absolute_url'."
            )

        if description is None:
            description = ""

        if not isinstance(description, str):
            raise JobSourcePayloadError(
                "Greenhouse job 'content' must be text."
            )

        if posted_at is not None and not isinstance(posted_at, str):
            raise JobSourcePayloadError(
                "Greenhouse job 'updated_at' must be text or null."
            )

        try:
            return RawJobPosting(
                external_id=str(external_id),
                company_name=source.company_name,
                title=title.strip(),
                location=location,
                description=description,
                application_url=application_url,
                posted_at=posted_at,
                source_provider=JobSourceProvider.GREENHOUSE,
                source_identifier=source.source_identifier,
            )

        except ValidationError as exc:
            raise JobSourcePayloadError(
                "Greenhouse job could not be converted into "
                "a valid raw job posting."
            ) from exc

    def _extract_location(
        self,
        job: dict[str, Any],
    ) -> str | None:
        location = job.get("location")

        if location is None:
            return None

        if not isinstance(location, dict):
            raise JobSourcePayloadError(
                "Greenhouse job 'location' must be an object or null."
            )

        name = location.get("name")

        if name is None:
            return None

        if not isinstance(name, str):
            raise JobSourcePayloadError(
                "Greenhouse location name must be text or null."
            )

        normalized_name = name.strip()

        return normalized_name or None