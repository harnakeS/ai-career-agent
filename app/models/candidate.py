from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Represents the candidate being matched to jobs."""

    name: str

    years_experience: int

    graduation_year: int

    education: str

    majors: list[str]

    skills: list[str]

    programming_languages: list[str]

    frameworks: list[str]

    tools: list[str]

    certifications: list[str]

    preferred_locations: list[str]

    willing_to_relocate: bool

    us_citizen: bool

    desired_roles: list[str]