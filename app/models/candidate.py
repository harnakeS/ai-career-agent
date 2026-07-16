from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Structured candidate data used by the job-matching engine."""

    name: str

    graduation_year: int | None

    education: str
    majors: list[str]
    minors: list[str]

    programming_languages: list[str]
    frameworks: list[str]
    tools: list[str]
    skills: list[str]
    certifications: list[str]

    full_time_experience_months: int = Field(ge=0)
    internship_experience_months: int = Field(ge=0)
    co_op_experience_months: int = Field(ge=0)
    part_time_experience_months: int = Field(ge=0)
    contract_experience_months: int = Field(ge=0)

    preferred_locations: list[str]
    willing_to_relocate: bool
    us_citizen: bool
    desired_roles: list[str]