from dataclasses import dataclass

from app.models.candidate import CandidateProfile
from app.models.job import JobPosting


@dataclass(frozen=True)
class CategoryScore:
    """Score and explanation produced by one matching category."""

    score: float
    reasons: list[str]


def score_technical_skills(
    matched_skills: list[str],
) -> CategoryScore:
    """Score the number of candidate technologies found in the posting."""

    score = min(len(matched_skills) * 8, 55)

    if matched_skills:
        reasons = [
            f"Matched technologies: {', '.join(matched_skills)}."
        ]
    else:
        reasons = [
            "No explicit candidate technologies were matched."
        ]

    return CategoryScore(
        score=float(score),
        reasons=reasons,
    )


def score_role_alignment(
    matched_roles: list[str],
) -> CategoryScore:
    """Score whether the job title aligns with a desired role."""

    score = 25 if matched_roles else 0

    reasons: list[str] = []

    if matched_roles:
        reasons.append(
            f"Job title aligns with: {', '.join(matched_roles)}."
        )

    return CategoryScore(
        score=float(score),
        reasons=reasons,
    )


def score_location(
    candidate: CandidateProfile,
    location_match: bool,
) -> CategoryScore:
    """Score the job location against candidate preferences."""

    if location_match:
        return CategoryScore(
            score=10.0,
            reasons=["Location matches a stated preference."],
        )

    if candidate.willing_to_relocate:
        return CategoryScore(
            score=5.0,
            reasons=[
                "Location is outside preferences, but relocation is allowed."
            ],
        )

    return CategoryScore(
        score=0.0,
        reasons=["Location does not match candidate preferences."],
    )


def score_early_career(
    job: JobPosting,
    early_career_match: bool,
) -> CategoryScore:
    """Score whether the posting contains early-career language."""

    if early_career_match:
        return CategoryScore(
            score=10.0,
            reasons=["Posting contains early-career language."],
        )

    return CategoryScore(
        score=0.0,
        reasons=[],
    )