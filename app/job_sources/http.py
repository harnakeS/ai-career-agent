import json
from json import JSONDecodeError
from typing import Any, Protocol, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.job_sources.errors import (
    JobSourcePayloadError,
    JobSourceRequestError,
)


JsonObject = dict[str, Any]


@runtime_checkable
class JsonHttpClient(Protocol):
    """Contract for retrieving JSON objects over HTTP."""

    def get_json(self, url: str) -> JsonObject:
        """Retrieve a URL and return its JSON object response."""
        ...


class UrllibJsonHttpClient:
    """Standard-library JSON HTTP client used by real job sources."""

    def __init__(
        self,
        timeout_seconds: float = 15.0,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")

        self._timeout_seconds = timeout_seconds

    def get_json(self, url: str) -> JsonObject:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "AI-Job-Scout/1.0",
            },
        )

        try:
            with urlopen(
                request,
                timeout=self._timeout_seconds,
            ) as response:
                payload = json.load(response)

        except (HTTPError, URLError, TimeoutError) as exc:
            raise JobSourceRequestError(
                f"Unable to retrieve job-source URL: {url}"
            ) from exc

        except JSONDecodeError as exc:
            raise JobSourcePayloadError(
                f"Job-source response was not valid JSON: {url}"
            ) from exc

        if not isinstance(payload, dict):
            raise JobSourcePayloadError(
                "Expected the job-source response to be a JSON object."
            )

        return payload