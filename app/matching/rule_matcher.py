import re
from dataclasses import dataclass

from app.models.candidate import CandidateProfile
from app.models.job import JobPosting


@dataclass(frozen=True)
class MatchResult:
    """Result produced by the deterministic job matcher."""

    score: float
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

    reasons: list[str] = []

    # Technical alignment: maximum 55 points.
    technical_score = min(len(matched_skills) * 8, 55)

    if matched_skills:
        reasons.append(
            f"Matched technologies: {', '.join(matched_skills)}."
        )
    else:
        reasons.append("No explicit candidate technologies were matched.")

    # Desired-role alignment: maximum 25 points.
    role_score = 25 if matched_roles else 0

    if matched_roles:
        reasons.append(
            f"Job title aligns with: {', '.join(matched_roles)}."
        )

    # Location alignment: maximum 10 points.
    location_score = 10 if location_match else 0

    if location_match:
        reasons.append("Location matches a stated preference.")
    elif candidate.willing_to_relocate:
        location_score = 5
        reasons.append("Location is outside preferences, but relocation is allowed.")

    # Early-career language: maximum 10 points.
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

    early_career_score = 10 if early_career_match else 0

    if early_career_match:
        reasons.append("Posting contains early-career language.")

    total_score = min(
        technical_score
        + role_score
        + location_score
        + early_career_score,
        100,
    )

    return MatchResult(
        score=float(total_score),
        matched_skills=matched_skills,
        matched_roles=matched_roles,
        location_match=location_match,
        reasons=reasons,
    )