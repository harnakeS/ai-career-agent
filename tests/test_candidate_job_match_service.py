from app.matching.service import (
    CandidateJobMatchService,
)
from app.models.candidate_evidence import (
    CandidateEvidence,
    CandidateEvidenceCollection,
    EvidenceCategory,
    EvidenceSourceType,
)
from app.models.job import JobPosting
from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.extractor import (
    StubRequirementsExtractor,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
)


def create_job() -> JobPosting:
    return JobPosting(
        company="Example Company",
        requisition_id="REQ-123",
        title="Software Engineer",
        location="New York, NY",
        description=(
            "Python and Kubernetes are required."
        ),
        application_url=(
            "https://example.com/jobs/REQ-123"
        ),
    )


def create_evidence() -> CandidateEvidenceCollection:
    return CandidateEvidenceCollection(
        evidence=[
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="Python",
                source_type=EvidenceSourceType.SKILLS,
                source_name="Programming Languages",
                evidence_text="Python",
            )
        ]
    )


def create_service() -> CandidateJobMatchService:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            requirements=[
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=(
                        RequirementImportance.REQUIRED
                    ),
                    value="Python",
                    source_text=(
                        "Python is required."
                    ),
                ),
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=(
                        RequirementImportance.REQUIRED
                    ),
                    value="Kubernetes",
                    source_text=(
                        "Kubernetes is required."
                    ),
                ),
            ],
            entry_level=True,
        )
    )

    requirements_service = (
        RequirementsExtractionService(
            extractor
        )
    )

    return CandidateJobMatchService(
        requirements_service=requirements_service
    )


def test_matches_extracted_requirements_to_evidence() -> None:
    result = create_service().match(
        create_job(),
        create_evidence(),
    )

    assert len(result.requirements.requirements) == 2
    assert result.requirements.entry_level is True
    assert result.matched_count == 1
    assert result.unmatched_count == 1
    assert result.unevaluated_count == 0
    assert result.overlap_count == 1
    assert len(result.description_overlaps.overlaps) == 1
    assert (
        result.description_overlaps
        .overlaps[0]
        .evidence.value
        == "Python"
    )

    matched = (
        result.evidence_matches
        .matched_requirements[0]
    )
    unmatched = (
        result.evidence_matches
        .unmatched_requirements[0]
    )

    assert matched.requirement.value == "Python"
    assert matched.evidence[0].value == "Python"
    assert unmatched.requirement.value == "Kubernetes"


def test_preserves_selected_job_in_match_result() -> None:
    job = create_job()

    result = create_service().match(
        job,
        create_evidence(),
    )

    assert result.job is job
    assert result.job.requisition_id == "REQ-123"

def test_preserves_explicit_overlap_when_requirement_is_not_extracted(
) -> None:
    job = JobPosting(
        company="Example Company",
        requisition_id="REQ-456",
        title="Data Analyst",
        location="New York, NY",
        description=(
            "Candidates should have experience using SQL."
        ),
        application_url=(
            "https://example.com/jobs/REQ-456"
        ),
    )

    evidence = CandidateEvidenceCollection(
        evidence=[
            CandidateEvidence(
                category=EvidenceCategory.SKILL,
                value="SQL",
                source_type=EvidenceSourceType.SKILLS,
                source_name="Programming Languages",
                evidence_text="SQL",
            )
        ]
    )

    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            requirements=[],
            entry_level=True,
        )
    )

    service = CandidateJobMatchService(
        requirements_service=RequirementsExtractionService(
            extractor
        )
    )

    result = service.match(job, evidence)

    assert result.matched_count == 0
    assert result.unmatched_count == 0
    assert result.overlap_count == 1
    assert (
        result.description_overlaps
        .overlaps[0]
        .evidence.value
        == "SQL"
    )

def test_missing_preferred_requirement_is_not_required_gap() -> None:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            requirements=[
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=(
                        RequirementImportance.PREFERRED
                    ),
                    value="Kubernetes",
                    source_text=(
                        "Kubernetes experience is preferred."
                    ),
                ),
            ],
        )
    )

    service = CandidateJobMatchService(
        requirements_service=RequirementsExtractionService(
            extractor
        )
    )

    result = service.match(
        create_job(),
        create_evidence(),
    )

    assert result.unmatched_count == 1
    assert result.required_gap_count == 0
    assert result.non_required_missing_count == 1