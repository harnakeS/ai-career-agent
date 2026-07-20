from app.candidate.builder import CandidateEvidenceBuilder
from app.models.candidate_evidence import (
    EvidenceCategory,
    EvidenceSourceType,
)
from app.models.candidate import CandidateProfile


def create_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Harnake Sahi",
        graduation_year=2026,
        education="Bachelor of Arts",
        majors=["Computer Science"],
        minors=["Economics"],
        programming_languages=["Python", "Java"],
        frameworks=["Pandas"],
        tools=["Git", "Linux"],
        skills=["Machine Learning"],
        certifications=["Azure AI Engineer Associate"],
        full_time_experience_months=0,
        internship_experience_months=8,
        co_op_experience_months=0,
        part_time_experience_months=0,
        contract_experience_months=0,
        preferred_locations=["New Jersey", "New York"],
        willing_to_relocate=True,
        us_citizen=True,
        desired_roles=["Software Engineer", "AI Engineer"],
    )


def test_builder_creates_skill_evidence() -> None:
    collection = CandidateEvidenceBuilder().build(create_profile())

    skills = collection.by_category(EvidenceCategory.SKILL)

    assert collection.find_value("Python")
    assert collection.find_value("Java")
    assert collection.find_value("Pandas")
    assert collection.find_value("Git")
    assert collection.find_value("Machine Learning")
    assert len(skills) == 6


def test_builder_preserves_skill_source_group() -> None:
    collection = CandidateEvidenceBuilder().build(create_profile())

    python_evidence = collection.find_value("Python")

    assert len(python_evidence) == 1
    assert python_evidence[0].source_type == EvidenceSourceType.SKILLS
    assert python_evidence[0].source_name == "Programming Languages"


def test_builder_creates_education_evidence() -> None:
    collection = CandidateEvidenceBuilder().build(create_profile())

    education = collection.by_category(EvidenceCategory.EDUCATION)

    assert len(education) == 3
    assert collection.find_value("Bachelor of Arts")
    assert collection.find_value("Computer Science")
    assert collection.find_value("Economics")


def test_builder_creates_certification_evidence() -> None:
    collection = CandidateEvidenceBuilder().build(create_profile())

    certifications = collection.by_category(
        EvidenceCategory.CERTIFICATION
    )

    assert len(certifications) == 1
    assert certifications[0].value == "Azure AI Engineer Associate"


def test_builder_creates_only_nonzero_experience_evidence() -> None:
    collection = CandidateEvidenceBuilder().build(create_profile())

    experience = collection.by_category(EvidenceCategory.EXPERIENCE)

    assert len(experience) == 1
    assert experience[0].value == "8 months"
    assert experience[0].source_name == "Internship Experience"


def test_builder_ignores_blank_values() -> None:
    profile = create_profile()
    profile.programming_languages = ["Python", " ", ""]
    profile.certifications = [""]

    collection = CandidateEvidenceBuilder().build(profile)

    assert len(collection.find_value("Python")) == 1
    assert collection.by_category(EvidenceCategory.CERTIFICATION) == []