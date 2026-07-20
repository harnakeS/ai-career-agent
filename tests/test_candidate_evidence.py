from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
    EvidenceConfidence,
    EvidenceSourceType,
)


def test_candidate_evidence_defaults_to_high_confidence() -> None:
    evidence = CandidateEvidence(
        category=EvidenceCategory.SKILL,
        value="Python",
        source_type=EvidenceSourceType.SKILLS,
    )

    assert evidence.confidence == EvidenceConfidence.HIGH


def test_candidate_evidence_collection_filters_by_category() -> None:
    collection = CandidateEvidenceCollection(
        evidence=[
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="Python",
                source_type=EvidenceSourceType.SKILLS,
            ),
            CandidateEvidence(
                category=EvidenceCategory.CERTIFICATION,
                value="Azure AI Engineer Associate",
                source_type=EvidenceSourceType.CERTIFICATION,
            ),
        ]
    )

    result = collection.by_category(EvidenceCategory.SKILL)

    assert len(result) == 1
    assert result[0].value == "Python"


def test_candidate_evidence_collection_filters_by_source_type() -> None:
    collection = CandidateEvidenceCollection(
        evidence=[
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="Python",
                source_type=EvidenceSourceType.PROJECT,
                source_name="NBA Match Predictor",
            ),
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="SQL",
                source_type=EvidenceSourceType.SKILLS,
            ),
        ]
    )

    result = collection.by_source_type(EvidenceSourceType.PROJECT)

    assert len(result) == 1
    assert result[0].source_name == "NBA Match Predictor"


def test_candidate_evidence_collection_finds_value_case_insensitively() -> None:
    collection = CandidateEvidenceCollection(
        evidence=[
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="Python",
                source_type=EvidenceSourceType.SKILLS,
            )
        ]
    )

    result = collection.find_value(" python ")

    assert len(result) == 1
    assert result[0].value == "Python"


def test_candidate_evidence_collection_returns_empty_list_for_missing_value() -> None:
    collection = CandidateEvidenceCollection()

    result = collection.find_value("Docker")

    assert result == []