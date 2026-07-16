import re
from dataclasses import dataclass

from app.models.candidate import CandidateProfile
from app.models.job import JobPosting
from app.matching.components import (
    CategoryScore,
    score_early_career,
    score_experience_alignment,
    score_location,
    score_role_alignment,
    score_technical_skills,
)
from app.matching.scoring import (
    WeightedCategory,
    aggregate_scores,
    normalize_category_score,
)


@dataclass(frozen=True)
class MatchResult:
    """Result produced by the deterministic job matcher."""

    score: float

    technical_score: float
    role_score: float
    location_score: float
    early_career_score: float
    experience_score: float

    matched_skills: list[str]
    matched_roles: list[str]
    location_match: bool
    reasons: list[str]


def normalize_text(value: str) -> str:
    """Lowercase text and replace punctuation with spaces."""
    return re.sub(r"[^a-z0-9+#.]+", " ", value.lower()).strip()


def term_appears(term: str, text: str) -> bool:
    """Check whether a complete normalized term appears in text."""
    normalized_term = normalize_text(term)
    normalized_text = normalize_text(text)

    if not normalized_term:
        return False

    pattern = rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])"

    return re.search(pattern, normalized_text) is not None


def calculate_rule_match(
    candidate: CandidateProfile,
    job: JobPosting,
) -> MatchResult:
    """Score a job against a candidate profile using deterministic rules."""

    searchable_job_text = " ".join(
        [
            job.title,
            job.description,
            job.location or "",
        ]
    )

    candidate_technologies = list(
        dict.fromkeys(
            candidate.skills
            + candidate.programming_languages
            + candidate.frameworks
            + candidate.tools
            + candidate.certifications
        )
    )

    matched_skills = [
        skill
        for skill in candidate_technologies
        if term_appears(skill, searchable_job_text)
    ]

    matched_roles = [
        role
        for role in candidate.desired_roles
        if term_appears(role, job.title)
    ]

    location_match = any(
        term_appears(location, job.location or "")
        for location in candidate.preferred_locations
    )

    technical_result = score_technical_skills(matched_skills)

    experience_result = score_experience_alignment(
        candidate,
        job,
    )

    role_result = score_role_alignment(matched_roles)

    location_result = score_location(
        candidate,
        location_match,
    )

    early_career_terms = [
        "entry level",
        "early career",
        "new grad",
        "new graduate",
        "recent graduate",
        "associate",
        "junior",
        "software engineer i",
    ]

    early_career_match = any(
        term_appears(term, searchable_job_text)
        for term in early_career_terms
    )

    early_career_result = score_early_career(
        job,
        early_career_match,
    )

    normalized_technical = CategoryScore(
        score=normalize_category_score(
            technical_result,
            original_max=55.0,
            target_max=35.0,
        ),
        reasons=technical_result.reasons,
    )

    normalized_experience = CategoryScore(
        score=normalize_category_score(
            experience_result,
            original_max=20.0,
            target_max=20.0,
        ),
        reasons=experience_result.reasons,
    )

    normalized_role = CategoryScore(
        score=normalize_category_score(
            role_result,
            original_max=25.0,
            target_max=10.0,
        ),
        reasons=role_result.reasons,
    )

    normalized_location = CategoryScore(
        score=normalize_category_score(
            location_result,
            original_max=10.0,
            target_max=5.0,
        ),
        reasons=location_result.reasons,
    )

    normalized_early_career = CategoryScore(
        score=normalize_category_score(
            early_career_result,
            original_max=10.0,
            target_max=10.0,
        ),
        reasons=early_career_result.reasons,
    )

    aggregated = aggregate_scores(
        [
            WeightedCategory(
                name="technical",
                result=normalized_technical,
                max_points=35.0,
            ),
            WeightedCategory(
                name="experience",
                result=normalized_experience,
                max_points=20.0,
            ),
            WeightedCategory(
                name="role",
                result=normalized_role,
                max_points=10.0,
            ),
            WeightedCategory(
                name="location",
                result=normalized_location,
                max_points=5.0,
            ),
            WeightedCategory(
                name="early_career",
                result=normalized_early_career,
                max_points=10.0,
            ),
        ]
    )

    return MatchResult(
        score=aggregated.score,
        technical_score=normalized_technical.score,
        experience_score=normalized_experience.score,
        role_score=normalized_role.score,
        location_score=normalized_location.score,
        early_career_score=normalized_early_career.score,
        matched_skills=matched_skills,
        matched_roles=matched_roles,
        location_match=location_match,
        reasons=aggregated.reasons,
    )