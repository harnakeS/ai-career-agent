import re

from app.models.candidate import CandidateProfile
from app.parsing.experience_parser import EmploymentType
from app.parsing.resume_parser import ParsedResume


def extract_candidate_name(header: str) -> str:
    """Extract the candidate name from the first non-empty header line."""

    for line in header.splitlines():
        cleaned_line = line.strip()

        if cleaned_line:
            return cleaned_line

    raise ValueError("Candidate name could not be extracted from resume header.")


def sum_experience_months(
    resume: ParsedResume,
    employment_type: EmploymentType,
) -> int:
    """Sum known experience months for one employment category."""

    return sum(
        experience.duration_months or 0
        for experience in resume.experiences
        if experience.employment_type == employment_type
    )


def infer_desired_roles(resume: ParsedResume) -> list[str]:
    """Infer reasonable target roles from parsed resume content."""

    searchable_text = " ".join(
        [
            *resume.skills.programming_languages,
            *resume.skills.frameworks,
            *resume.skills.tools,
            *resume.skills.concepts,
            *resume.skills.certifications,
            *[
                project.name
                for project in resume.projects
            ],
            *[
                technology
                for project in resume.projects
                for technology in project.technologies
            ],
        ]
    ).lower()

    desired_roles = [
        "Software Engineer",
        "Backend Engineer",
        "Technology Analyst",
        "IT Analyst",
        "Application Developer",
        "Application Support Engineer",
    ]

    if any(
        term in searchable_text
        for term in [
            "machine learning",
            "scikit-learn",
            "ai engineer",
        ]
    ):
        desired_roles.extend(
            [
                "AI Engineer",
                "Machine Learning Engineer",
            ]
        )

    if any(
        term in searchable_text
        for term in [
            "sql",
            "pandas",
            "data pipeline",
        ]
    ):
        desired_roles.append("Data Engineer")

    return list(dict.fromkeys(desired_roles))


def build_candidate_profile(
    resume: ParsedResume,
    *,
    preferred_locations: list[str],
    willing_to_relocate: bool,
    us_citizen: bool,
) -> CandidateProfile:
    """Build a candidate profile from parsed resume data and preferences."""

    minors = (
        [resume.education.minor]
        if resume.education.minor
        else []
    )

    return CandidateProfile(
        name=extract_candidate_name(resume.sections.header),
        graduation_year=resume.education.graduation_year,
        education=resume.education.degree,
        majors=[resume.education.major],
        minors=minors,
        programming_languages=resume.skills.programming_languages,
        frameworks=resume.skills.frameworks,
        tools=resume.skills.tools,
        skills=resume.skills.concepts,
        certifications=resume.skills.certifications,
        full_time_experience_months=sum_experience_months(
            resume,
            EmploymentType.FULL_TIME,
        ),
        internship_experience_months=sum_experience_months(
            resume,
            EmploymentType.INTERNSHIP,
        ),
        co_op_experience_months=sum_experience_months(
            resume,
            EmploymentType.CO_OP,
        ),
        part_time_experience_months=sum_experience_months(
            resume,
            EmploymentType.PART_TIME,
        ),
        contract_experience_months=sum_experience_months(
            resume,
            EmploymentType.CONTRACT,
        ),
        preferred_locations=preferred_locations,
        willing_to_relocate=willing_to_relocate,
        us_citizen=us_citizen,
        desired_roles=infer_desired_roles(resume),
    )