from typing import Protocol, runtime_checkable

from app.job_sources.models import (
    CompanySource,
    RawJobPosting,
)


@runtime_checkable
class JobSource(Protocol):
    """
    Contract implemented by every job-source provider.

    A job source receives one configured company source and returns
    provider-neutral raw job postings for that company.
    """

    def collect(
        self,
        source: CompanySource,
    ) -> list[RawJobPosting]:
        """Collect all currently available jobs from the configured source."""
        ...