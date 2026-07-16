from pydantic import BaseModel, Field


class CandidatePreferences(BaseModel):
    """User-provided preferences that should not be inferred from a resume."""

    preferred_locations: list[str] = Field(min_length=1)
    willing_to_relocate: bool
    us_citizen: bool