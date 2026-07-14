from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobPosting(BaseModel):
    """Standard representation of a job posting from any career site."""

    model_config = ConfigDict(str_strip_whitespace=True)

    company: str = Field(min_length=1, max_length=100)
    requisition_id: str = Field(min_length=1, max_length=150)
    title: str = Field(min_length=1, max_length=250)

    location: str | None = None
    description: str = Field(min_length=1)

    application_url: HttpUrl
    date_posted: date | None = None

    date_discovered: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )