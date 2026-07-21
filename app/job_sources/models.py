from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


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
    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    company_name: str = Field(min_length=1)
    provider: JobSourceProvider
    source_identifier: str = Field(min_length=1)
    careers_url: HttpUrl
    enabled: bool = True

class CompanySourceConfiguration(BaseModel):
    """Validated collection of selected company sources."""

    sources: list[CompanySource] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_sources(
        self,
    ) -> "CompanySourceConfiguration":
        seen_sources: set[
            tuple[JobSourceProvider, str]
        ] = set()

        for source in self.sources:
            source_key = (
                source.provider,
                source.source_identifier.casefold(),
            )

            if source_key in seen_sources:
                raise ValueError(
                    "Company-source configuration contains "
                    "a duplicate provider and source identifier: "
                    f"'{source.provider.value}' and "
                    f"'{source.source_identifier}'."
                )

            seen_sources.add(source_key)

        return self


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
    published_at: str | None = None
    updated_at: str | None = None
    source_provider: JobSourceProvider
    source_identifier: str