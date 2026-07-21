from typing import cast

import pytest

from app.candidate.service import (
    CandidateResumeService,
)
from app.models.candidate import CandidateProfile
from app.models.candidate_evidence import (
    EvidenceCategory,
)
from app.models.preferences import (
    CandidatePreferences,
)
from app.parsing.pdf_parser import (
    ResumeParsingError,
)
from app.parsing.resume_parser import (
    ParsedResume,
)


def create_preferences() -> CandidatePreferences:
    return CandidatePreferences(
        preferred_locations=[
            "New Jersey",
            "New York",
            "Philadelphia",
            "Remote",
        ],
        willing_to_relocate=True,
        us_citizen=True,
    )


def create_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Harnake Sahi",
        graduation_year=2026,
        education="Bachelor of Arts",
        majors=["Computer Science"],
        minors=["Economics"],
        programming_languages=[
            "Python",
            "Java",
            "SQL",
        ],
        frameworks=["Pandas"],
        tools=["Git", "Linux", "Azure"],
        skills=["Machine Learning"],
        certifications=[
            "Azure AI Engineer Associate"
        ],
        full_time_experience_months=0,
        internship_experience_months=10,
        co_op_experience_months=0,
        part_time_experience_months=0,
        contract_experience_months=0,
        preferred_locations=[
            "New Jersey",
            "New York",
            "Philadelphia",
            "Remote",
        ],
        willing_to_relocate=True,
        us_citizen=True,
        desired_roles=[
            "Software Engineer",
            "AI Engineer",
        ],
    )


def test_process_builds_profile_and_evidence(
    monkeypatch,
) -> None:
    parsed_resume = cast(
        ParsedResume,
        object(),
    )
    profile = create_profile()
    captured_arguments: dict[str, object] = {}

    monkeypatch.setattr(
        "app.candidate.service.parse_resume_bytes",
        lambda value: parsed_resume,
    )

    def stub_build_candidate_profile(
        resume: ParsedResume,
        *,
        preferred_locations: list[str],
        willing_to_relocate: bool,
        us_citizen: bool,
    ) -> CandidateProfile:
        captured_arguments.update({
            "resume": resume,
            "preferred_locations": preferred_locations,
            "willing_to_relocate": willing_to_relocate,
            "us_citizen": us_citizen,
        })

        return profile

    monkeypatch.setattr(
        "app.candidate.service."
        "build_candidate_profile",
        stub_build_candidate_profile,
    )

    result = CandidateResumeService().process(
        b"uploaded-pdf",
        create_preferences(),
    )

    assert result.parsed_resume is parsed_resume
    assert result.profile == profile
    assert result.evidence.find_value("Python")
    assert result.evidence.find_value(
        "Azure AI Engineer Associate"
    )

    experience = result.evidence.by_category(
        EvidenceCategory.EXPERIENCE
    )

    assert len(experience) == 1
    assert experience[0].value == "10 months"

    assert captured_arguments == {
        "resume": parsed_resume,
        "preferred_locations": [
            "New Jersey",
            "New York",
            "Philadelphia",
            "Remote",
        ],
        "willing_to_relocate": True,
        "us_citizen": True,
    }


def test_process_propagates_resume_parsing_error(
    monkeypatch,
) -> None:
    def reject_resume(
        value: bytes,
    ) -> ParsedResume:
        raise ResumeParsingError(
            "No readable text was found in the PDF."
        )

    monkeypatch.setattr(
        "app.candidate.service.parse_resume_bytes",
        reject_resume,
    )

    with pytest.raises(
        ResumeParsingError,
        match="No readable text",
    ):
        CandidateResumeService().process(
            b"invalid-pdf",
            create_preferences(),
        )