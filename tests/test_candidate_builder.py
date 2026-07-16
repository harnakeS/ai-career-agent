from app.parsing.candidate_builder import (
    build_candidate_profile,
    extract_candidate_name,
    infer_desired_roles,
    sum_experience_months,
)
from app.parsing.resume.education_parser import ParsedEducation
from app.parsing.resume.experience_parser import (
    EmploymentType,
    ParsedExperience,
)
from app.parsing.resume.project_parser import ParsedProject
from app.parsing.resume_parser import ParsedResume
from app.parsing.resume.section_parser import ResumeSections
from app.parsing.resume.skills_parser import ParsedSkills


def create_parsed_resume() -> ParsedResume:
    sections = ResumeSections(
        header="Harnake Sahi\nexample@email.com",
        education="Example education section",
        skills="Example skills section",
        work_experience="Example experience section",
        projects="Example projects section",
    )

    skills = ParsedSkills(
        programming_languages=["Python", "Java", "SQL"],
        frameworks=["Pandas", "Scikit-learn"],
        tools=["Git", "Linux", "Azure"],
        concepts=["Machine Learning"],
        certifications=["Azure AI Engineer Associate"],
    )

    education = ParsedEducation(
        degree="Bachelor of Arts",
        major="Computer Science",
        minor="Economics",
        institution="Rutgers University",
        graduation_year=2026,
    )

    experiences = [
        ParsedExperience(
            company="Example Company",
            title="Software Engineering Intern",
            employment_type=EmploymentType.INTERNSHIP,
            employment_type_confidence=1.0,
            employment_type_reason=(
                "Job title explicitly contains internship language."
            ),
            start_month=5,
            start_year=2025,
            end_month=9,
            end_year=2025,
            duration_months=5,
            location="New York, NY",
            bullets=["Built internal software tools."],
        ),
        ParsedExperience(
            company="Another Company",
            title="Data Intern",
            employment_type=EmploymentType.INTERNSHIP,
            employment_type_confidence=1.0,
            employment_type_reason=(
                "Job title explicitly contains internship language."
            ),
            start_month=5,
            start_year=2024,
            end_month=9,
            end_year=2024,
            duration_months=5,
            location="New Jersey",
            bullets=["Built SQL reporting workflows."],
        ),
    ]

    projects = [
        ParsedProject(
            name="Machine Learning Predictor",
            start_month=11,
            start_year=2024,
            end_month=12,
            end_year=2024,
            duration_months=2,
            technologies=[
                "Python",
                "Pandas",
                "Scikit-learn",
            ],
            bullets=[
                "Built a machine-learning prediction pipeline."
            ],
        )
    ]

    return ParsedResume(
        raw_text="Raw resume text",
        cleaned_text="Cleaned resume text",
        sections=sections,
        skills=skills,
        education=education,
        experiences=experiences,
        projects=projects,
    )


def test_extract_candidate_name_uses_first_header_line() -> None:
    name = extract_candidate_name(
        "\nHarnake Sahi\nexample@email.com"
    )

    assert name == "Harnake Sahi"


def test_sum_experience_months_separates_employment_types() -> None:
    resume = create_parsed_resume()

    assert (
        sum_experience_months(
            resume,
            EmploymentType.INTERNSHIP,
        )
        == 10
    )

    assert (
        sum_experience_months(
            resume,
            EmploymentType.FULL_TIME,
        )
        == 0
    )


def test_infer_desired_roles_from_resume_content() -> None:
    resume = create_parsed_resume()

    roles = infer_desired_roles(resume)

    assert "Software Engineer" in roles
    assert "AI Engineer" in roles
    assert "Machine Learning Engineer" in roles
    assert "Data Engineer" in roles


def test_build_candidate_profile_from_parsed_resume() -> None:
    resume = create_parsed_resume()

    candidate = build_candidate_profile(
        resume,
        preferred_locations=[
            "New Jersey",
            "New York",
            "Remote",
        ],
        willing_to_relocate=True,
        us_citizen=True,
    )

    assert candidate.name == "Harnake Sahi"
    assert candidate.graduation_year == 2026
    assert candidate.education == "Bachelor of Arts"
    assert candidate.majors == ["Computer Science"]
    assert candidate.minors == ["Economics"]

    assert candidate.programming_languages == [
        "Python",
        "Java",
        "SQL",
    ]

    assert candidate.internship_experience_months == 10
    assert candidate.full_time_experience_months == 0

    assert candidate.preferred_locations == [
        "New Jersey",
        "New York",
        "Remote",
    ]

    assert candidate.willing_to_relocate
    assert candidate.us_citizen