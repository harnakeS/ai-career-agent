import re
from dataclasses import dataclass

from app.models.candidate import CandidateProfile
from app.models.job import JobPosting
from app.matching.components import (
    score_early_career,
    score_location,
    score_role_alignment,
    score_technical_skills,
)


@dataclass(frozen=True)
class MatchResult:
    """Result produced by the deterministic job matcher."""

    score: float

    technical_score: float
    role_score: float
    location_score: float
    early_career_score: float

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
    role_result = score_role_alignment(matched_roles)
    location_result = score_location(candidate, location_match)

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

    total_score = min(
        technical_result.score
        + role_result.score
        + location_result.score
        + early_career_result.score,
        100,
    )

    reasons = (
        technical_result.reasons
        + role_result.reasons
        + location_result.reasons
        + early_career_result.reasons
    )

    return MatchResult(
        score=float(total_score),
        technical_score=technical_result.score,
        role_score=role_result.score,
        location_score=location_result.score,
        early_career_score=early_career_result.score,
        matched_skills=matched_skills,
        matched_roles=matched_roles,
        location_match=location_match,
        reasons=reasons,
    )