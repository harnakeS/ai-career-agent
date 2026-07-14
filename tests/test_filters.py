from app.models.job import JobPosting
from app.processing.filters import (
    extract_minimum_experience,
    is_potential_match,
    title_is_excluded,
)


def create_job(title: str, description: str) -> JobPosting:
    return JobPosting(
        company="Example Company",
        requisition_id="123",
        title=title,
        location="Remote",
        description=description,
        application_url="https://example.com/job",
    )


def test_excludes_senior_titles():
    assert title_is_excluded("Senior Software Engineer")
    assert title_is_excluded("Principal Data Engineer")
    assert not title_is_excluded("Software Engineer I")


def test_extracts_experience():
    description = "Candidates should have at least 3 years of experience."

    assert extract_minimum_experience(description) == 3


def test_accepts_entry_level_job():
    job = create_job(
        "Software Engineer",
        "Bachelor's degree required.",
    )

    result, _ = is_potential_match(job)

    assert result


def test_rejects_five_year_requirement():
    job = create_job(
        "Software Engineer",
        "Minimum of 5 years of experience required.",
    )

    result, _ = is_potential_match(job)

    assert not result