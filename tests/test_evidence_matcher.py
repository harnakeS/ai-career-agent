from app.matching.evidence_matcher import EvidenceMatcher
from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
    EvidenceSourceType,
)
from app.models.job_requirements import (
    JobRequirements,
    Requirement,
    RequirementCategory,
    RequirementImportance,
)


def create_requirement(
    value: str,
    category: RequirementCategory = RequirementCategory.SKILL,
) -> Requirement:
    return Requirement(
        category=category,
        importance=RequirementImportance.REQUIRED,
        value=value,
        source_text=value,
    )


def create_evidence(
    value: str,
    category: EvidenceCategory = EvidenceCategory.SKILL,
) -> CandidateEvidence:
    return CandidateEvidence(
        category=category,
        value=value,
        source_type=EvidenceSourceType.SKILLS,
        source_name="Resume Skills",
        evidence_text=value,
    )


def test_matches_exact_skill() -> None:
    requirement = create_requirement("Python")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("Python")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is True
    assert len(result.evidence) == 1
    assert result.evidence[0].value == "Python"


def test_matching_is_case_insensitive() -> None:
    requirement = create_requirement("python")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("PYTHON")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is True


def test_matching_normalizes_whitespace() -> None:
    requirement = create_requirement("Machine   Learning")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence(" machine learning ")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is True


def test_does_not_match_different_value() -> None:
    requirement = create_requirement("Python")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("Java")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is False
    assert result.evidence == []


def test_does_not_match_incompatible_category() -> None:
    requirement = create_requirement(
        value="Python",
        category=RequirementCategory.CERTIFICATION,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("Python", EvidenceCategory.SKILL)]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is False


def test_matches_all_job_requirements() -> None:
    requirements = JobRequirements(
        requirements=[
            create_requirement("Python"),
            create_requirement("Java"),
        ]
    )
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("Python")]
    )

    result = EvidenceMatcher().match(requirements, evidence)

    assert len(result.matches) == 2
    assert len(result.matched_requirements) == 1
    assert len(result.unmatched_requirements) == 1
    assert result.matched_requirements[0].requirement.value == "Python"
    assert result.unmatched_requirements[0].requirement.value == "Java"


def test_unsupported_requirement_category_is_unmatched() -> None:
    requirement = create_requirement(
        value="New Jersey",
        category=RequirementCategory.LOCATION,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("New Jersey")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is False
    assert "not supported" in result.reason