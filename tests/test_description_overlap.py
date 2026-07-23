from app.matching.description_overlap import (
    DescriptionEvidenceOverlapMatcher,
)
from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
    EvidenceSourceType,
)


def create_evidence(
    value: str,
    *,
    category: EvidenceCategory = EvidenceCategory.SKILL,
    source_type: EvidenceSourceType = EvidenceSourceType.SKILLS,
) -> CandidateEvidence:
    return CandidateEvidence(
        category=category,
        value=value,
        source_type=source_type,
        source_name="Resume",
        evidence_text=value,
    )


def test_finds_explicit_candidate_skills() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("SQL"),
            create_evidence("Python"),
            create_evidence("Java"),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        (
            "Candidates should have experience using SQL, "
            "Python, R, or another data science tool."
        ),
        evidence,
    )

    assert [
        overlap.evidence.value
        for overlap in result.overlaps
    ] == [
        "SQL",
        "Python",
    ]


def test_matching_is_case_insensitive() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("Machine Learning"),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        "Experience with MACHINE LEARNING is preferred.",
        evidence,
    )

    assert len(result.overlaps) == 1
    assert (
        result.overlaps[0].evidence.value
        == "Machine Learning"
    )


def test_short_skill_does_not_match_inside_other_words() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("R"),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        "Strong communication skills are required.",
        evidence,
    )

    assert result.overlaps == []


def test_excludes_experience_duration_evidence() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence(
                "10 months",
                category=EvidenceCategory.EXPERIENCE,
                source_type=EvidenceSourceType.EXPERIENCE,
            ),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        "At least 10 months of experience is required.",
        evidence,
    )

    assert result.overlaps == []


def test_deduplicates_equivalent_evidence_values() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("Python"),
            create_evidence("python"),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        "Python experience is required.",
        evidence,
    )

    assert len(result.overlaps) == 1
    assert result.overlaps[0].evidence.value == "Python"


def test_overlap_reason_is_explainable() -> None:
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("SQL"),
        ]
    )

    result = DescriptionEvidenceOverlapMatcher().match(
        "Experience using SQL is required.",
        evidence,
    )

    assert len(result.overlaps) == 1
    assert "SQL" in result.overlaps[0].reason
    assert "explicitly" in result.overlaps[0].reason