from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class JobSourceProvider(str, Enum):
    """Supported job-source provider types."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    SMARTRECRUITERS = "smartrecruiters"
    WORKDAY = "workday"
    CUSTOM = "custom"


class CompanySource(BaseModel):
    """Configuration describing where one company publishes jobs."""

    company_name: str = Field(min_length=1)
    provider: JobSourceProvider
    source_identifier: str = Field(min_length=1)
    careers_url: HttpUrl
    enabled: bool = True


class RawJobPosting(BaseModel):
    """
    Provider-level job data collected before conversion into the
    application's canonical JobPosting model.
    """

    external_id: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    location: str | None = None
    description: str
    application_url: HttpUrl
    posted_at: str | None = None
    source_provider: JobSourceProvider
    source_identifier: str