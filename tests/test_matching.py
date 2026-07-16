import pytest
from app.models.candidate import CandidateProfile
from app.matching.rule_matcher import (
    calculate_rule_match,
    term_appears,
)
from app.models.job import JobPosting
from app.matching.components import (
    extract_required_experience_months,
    score_experience_alignment,
)

candidate = CandidateProfile(
    name="Test Candidate",
    graduation_year=2026,
    education="Bachelor of Arts",
    majors=["Computer Science"],
    minors=["Economics"],
    programming_languages=[
        "Java",
        "Python",
        "C",
        "SQL",
    ],
    frameworks=[
        "Pandas",
        "BeautifulSoup",
        "Playwright",
        "Scikit-learn",
        "NumPy",
    ],
    tools=[
        "Git",
        "Linux",
        "Azure",
        "Jupyter Notebook",
    ],
    skills=[
        "Object-Oriented Programming",
        "Data Structures & Algorithms",
        "Machine Learning",
    ],
    certifications=[
        "Azure AI Engineer Associate",
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
        "Backend Engineer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Engineer",
        "Technology Analyst",
        "IT Analyst",
        "Application Developer",
        "Application Support Engineer",
    ],
)


def create_job(
    title: str,
    description: str,
    location: str = "New York, NY",
) -> JobPosting:
    return JobPosting(
        company="Example Company",
        requisition_id="JR1001",
        title=title,
        location=location,
        description=description,
        application_url="https://example.com/jobs/JR1001",
    )


def test_single_letter_skill_does_not_match_inside_word() -> None:
    assert not term_appears("C", "Build scalable applications.")


def test_single_letter_skill_matches_standalone_language() -> None:
    assert term_appears("C", "Experience programming in C is preferred.")


def test_matches_multiword_role() -> None:
    assert term_appears(
        "Software Engineer",
        "Junior Software Engineer",
    )


def test_high_score_for_strong_entry_level_match() -> None:
    job = create_job(
        title="Junior Software Engineer",
        description=(
            "Build software using Python, SQL, Git, Linux, and Azure. "
            "This is an entry-level opportunity."
        ),
    )

    result = calculate_rule_match(candidate, job)

    assert result.score == pytest.approx(75.5682, rel=1e-4)
    assert result.technical_score == pytest.approx(25.4545, rel=1e-4)
    assert result.experience_score == 10.0
    assert result.role_score == 10.0
    assert result.location_score == 5.0
    assert result.early_career_score == 10.0
    


def test_lower_score_for_unrelated_role() -> None:
    job = create_job(
        title="Marketing Coordinator",
        description="Manage advertising campaigns and social media content.",
        location="California",
    )

    result = calculate_rule_match(candidate, job)

    assert result.score < 30
    assert result.matched_skills == []
    assert result.matched_roles == []
    assert not result.location_match

def test_relocation_receives_partial_location_score() -> None:
    job = create_job(
        title="Software Engineer",
        description="Build applications using Python.",
        location="Austin, TX",
    )

    result = calculate_rule_match(candidate, job)

    assert result.location_score == 2.5
    assert not result.location_match
    assert any(
        "relocation is allowed" in reason
        for reason in result.reasons
    )

def test_extract_required_experience_from_plus_requirement() -> None:
    job = create_job(
        title="Software Engineer",
        description="Candidates should have 2+ years of relevant experience.",
    )

    assert extract_required_experience_months(job) == 24


def test_extract_required_experience_from_range() -> None:
    job = create_job(
        title="Software Engineer",
        description="Requires 1-3 years of professional experience.",
    )

    assert extract_required_experience_months(job) == 12


def test_extract_required_experience_returns_none() -> None:
    job = create_job(
        title="Software Engineer",
        description="Bachelor's degree preferred.",
    )

    assert extract_required_experience_months(job) is None


def test_full_time_experience_meets_requirement() -> None:
    experienced_candidate = candidate.model_copy(
        update={
            "full_time_experience_months": 24,
            "internship_experience_months": 0,
        }
    )

    job = create_job(
        title="Software Engineer",
        description="Requires 2 years of experience.",
    )

    result = score_experience_alignment(
        experienced_candidate,
        job,
    )

    assert result.score == 20.0


def test_internship_experience_satisfies_entry_level_role() -> None:
    early_candidate = candidate.model_copy(
        update={
            "internship_experience_months": 12,
        }
    )

    job = create_job(
        title="Software Engineer",
        description="Requires 1 year of relevant experience.",
    )

    result = score_experience_alignment(
        early_candidate,
        job,
    )

    assert result.score == 15.0


def test_partial_credit_for_internship_experience() -> None:
    job = create_job(
        title="Software Engineer",
        description="Requires 2 years of experience.",
    )

    result = score_experience_alignment(
        candidate,
        job,
    )

    assert result.score == 8.0


def test_no_credit_for_senior_experience_requirement() -> None:
    job = create_job(
        title="Senior Software Engineer",
        description="Requires 5 years of experience.",
    )

    result = score_experience_alignment(
        candidate,
        job,
    )

    assert result.score == 0.0


def test_neutral_score_when_requirement_not_specified() -> None:
    job = create_job(
        title="Software Engineer",
        description="Recent graduates encouraged to apply.",
    )

    result = score_experience_alignment(
        candidate,
        job,
    )

    assert result.score == 10.0