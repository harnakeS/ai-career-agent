from app.matching.evidence_matcher import EvidenceMatcher
from app.matching.normalizer import RequirementNormalizer
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
from app.vocabulary.models import (
    VocabularyCategory,
    VocabularyConcept,
)
from app.vocabulary.repository import (
    InMemoryVocabularyRepository,
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
    source_type: EvidenceSourceType = EvidenceSourceType.SKILLS,
) -> CandidateEvidence:
    return CandidateEvidence(
        category=category,
        value=value,
        source_type=source_type,
        source_name="Resume Evidence",
        evidence_text=value,
    )

def create_experience_evidence(
    value: str,
) -> CandidateEvidence:
    return create_evidence(
        value=value,
        category=EvidenceCategory.EXPERIENCE,
        source_type=EvidenceSourceType.EXPERIENCE,
    )


def create_matcher_with_vocabulary() -> EvidenceMatcher:
    vocabulary = InMemoryVocabularyRepository(
        concepts=[
            VocabularyConcept(
                category=VocabularyCategory.SKILL,
                canonical_value="JavaScript",
                aliases=["JS", "Java Script"],
            ),
            VocabularyConcept(
                category=VocabularyCategory.EDUCATION,
                canonical_value="Bachelor Degree",
                aliases=[
                    "Bachelor's Degree",
                    "Bachelor of Arts",
                    "Bachelor of Science",
                ],
            ),
        ]
    )

    normalizer = RequirementNormalizer(vocabulary=vocabulary)

    return EvidenceMatcher(normalizer=normalizer)


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


def test_direct_match_reason_is_explainable() -> None:
    requirement = create_requirement("Python")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("python")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is True
    assert "direct-value comparison" in result.reason


def test_matches_skill_alias_using_vocabulary() -> None:
    requirement = create_requirement("JS")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("JavaScript")]
    )

    result = create_matcher_with_vocabulary().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert len(result.evidence) == 1
    assert result.evidence[0].value == "JavaScript"


def test_vocabulary_match_reason_includes_canonical_concept() -> None:
    requirement = create_requirement("JS")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("Java Script")]
    )

    result = create_matcher_with_vocabulary().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert "canonical vocabulary concept" in result.reason
    assert "'javascript'" in result.reason


def test_matches_education_alias_using_vocabulary() -> None:
    requirement = create_requirement(
        value="Bachelor's Degree",
        category=RequirementCategory.EDUCATION,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence(
                value="Bachelor of Arts",
                category=EvidenceCategory.EDUCATION,
            )
        ]
    )

    result = create_matcher_with_vocabulary().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert result.evidence[0].value == "Bachelor of Arts"


def test_does_not_match_alias_without_vocabulary() -> None:
    requirement = create_requirement("JS")
    evidence = CandidateEvidenceCollection(
        evidence=[create_evidence("JavaScript")]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is False


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
        evidence=[
            create_evidence(
                "Python",
                EvidenceCategory.SKILL,
            )
        ]
    )

    result = EvidenceMatcher().match_requirement(requirement, evidence)

    assert result.matched is False


def test_vocabulary_resolution_remains_category_aware() -> None:
    requirement = create_requirement(
        value="JavaScript",
        category=RequirementCategory.EDUCATION,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence(
                value="JS",
                category=EvidenceCategory.EDUCATION,
            )
        ]
    )

    result = create_matcher_with_vocabulary().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is False


def test_returns_all_matching_evidence_items() -> None:
    requirement = create_requirement("JavaScript")
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_evidence("JavaScript"),
            create_evidence("JS"),
            create_evidence("Python"),
        ]
    )

    result = create_matcher_with_vocabulary().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert len(result.evidence) == 2
    assert {item.value for item in result.evidence} == {
        "JavaScript",
        "JS",
    }


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

def test_matches_equivalent_experience_duration() -> None:
    requirement = create_requirement(
        value="1 year of experience",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_experience_evidence("12 months"),
        ]
    )

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert len(result.evidence) == 1
    assert "12 month(s)" in result.reason


def test_matches_when_experience_exceeds_requirement() -> None:
    requirement = create_requirement(
        value="6 months of experience",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_experience_evidence("12 months"),
        ]
    )

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True


def test_combines_multiple_experience_evidence_items() -> None:
    requirement = create_requirement(
        value="1 year of experience",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_experience_evidence("8 months"),
            create_experience_evidence("4 months"),
        ]
    )

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert len(result.evidence) == 2
    assert "12 month(s)" in result.reason


def test_does_not_match_insufficient_experience() -> None:
    requirement = create_requirement(
        value="2 years of experience",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_experience_evidence("8 months"),
        ]
    )

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is False
    assert result.evidence == []
    assert "8 month(s)" in result.reason
    assert "24 month(s)" in result.reason


def test_duration_requirement_without_experience_evidence_is_unmatched() -> None:
    requirement = create_requirement(
        value="1 year of experience",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection()

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is False
    assert result.evidence == []
    assert "0 month(s)" in result.reason


def test_nonduration_experience_uses_normal_matching() -> None:
    requirement = create_requirement(
        value="Distributed Systems",
        category=RequirementCategory.EXPERIENCE,
    )
    evidence = CandidateEvidenceCollection(
        evidence=[
            create_experience_evidence("distributed systems"),
        ]
    )

    result = EvidenceMatcher().match_requirement(
        requirement,
        evidence,
    )

    assert result.matched is True
    assert "direct-value comparison" in result.reason