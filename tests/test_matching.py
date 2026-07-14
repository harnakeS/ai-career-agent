from app.config.candidate import candidate
from app.matching.rule_matcher import (
    calculate_rule_match,
    term_appears,
)
from app.models.job import JobPosting


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

    assert result.score == 85.0
    assert "Python" in result.matched_skills
    assert "SQL" in result.matched_skills
    assert "C" not in result.matched_skills
    assert "Software Engineer" in result.matched_roles
    assert result.location_match


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