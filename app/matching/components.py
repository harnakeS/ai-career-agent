import re
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

def extract_required_experience_months(
    job: JobPosting,
) -> int | None:
    """Extract the lowest explicit experience requirement in months."""

    searchable_text = f"{job.title} {job.description}".lower()

    patterns = [
        r"(\d+)\+?\s+years? of (?:professional |relevant )?experience",
        r"at least\s+(\d+)\s+years?",
        r"minimum of\s+(\d+)\s+years?",
        r"minimum\s+(\d+)\s+years?",
        r"(\d+)\s*[-–—]\s*(\d+)\s+years?",
    ]

    required_years: list[int] = []

    for pattern in patterns:
        matches = re.findall(pattern, searchable_text)

        for match in matches:
            if isinstance(match, tuple):
                required_years.append(int(match[0]))
            else:
                required_years.append(int(match))

    if not required_years:
        return None

    return min(required_years) * 12


def score_experience_alignment(
    candidate: CandidateProfile,
    job: JobPosting,
) -> CategoryScore:
    """Score experience while keeping internships separate from full-time work."""

    required_months = extract_required_experience_months(job)

    full_time_months = candidate.full_time_experience_months

    early_career_months = (
        candidate.internship_experience_months
        + candidate.co_op_experience_months
        + candidate.part_time_experience_months
        + candidate.contract_experience_months
    )

    if required_months is None:
        return CategoryScore(
            score=10.0,
            reasons=[
                "No explicit minimum experience requirement was found."
            ],
        )

    if full_time_months >= required_months:
        return CategoryScore(
            score=20.0,
            reasons=[
                "Full-time experience meets the stated requirement."
            ],
        )

    total_relevant_months = full_time_months + early_career_months

    if required_months <= 24 and total_relevant_months >= required_months:
        return CategoryScore(
            score=15.0,
            reasons=[
                "Relevant internship and other experience align with "
                "the early-career requirement."
            ],
        )

    if required_months <= 24 and early_career_months > 0:
        return CategoryScore(
            score=8.0,
            reasons=[
                "The candidate has relevant internship experience but "
                "does not fully meet the stated experience requirement."
            ],
        )

    return CategoryScore(
        score=0.0,
        reasons=[
            "The candidate does not meet the stated minimum "
            "experience requirement."
        ],
    )