from app.models.job import JobPosting
from app.models.job_requirements import (
    JobRequirements,
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
        source="test",
        external_id="job-123",
        requisition_id="REQ-123",
        company="Example Company",
        title="Operations Manager",
        location="New York, NY",
        description=(
            "Inventory management experience is required. "
            "Forklift certification is preferred."
        ),
        application_url="https://example.com/jobs/job-123",
    )


def test_service_extracts_and_converts_job_requirements() -> None:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            requirements=[
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=RequirementImportance.REQUIRED,
                    value="  Inventory Management  ",
                    source_text=(
                        "Inventory management experience is required."
                    ),
                ),
                ExtractedRequirement(
                    category=RequirementCategory.CERTIFICATION,
                    importance=RequirementImportance.PREFERRED,
                    value="Forklift Certification",
                    source_text=(
                        "Forklift certification is preferred."
                    ),
                ),
            ]
        )
    )

    service = RequirementsExtractionService(extractor)

    result = service.extract(create_job())

    assert len(result.requirements) == 2
    assert result.requirements[0].value == "Inventory Management"
    assert result.requirements[1].value == "Forklift Certification"


def test_service_applies_converter_deduplication() -> None:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            requirements=[
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=RequirementImportance.PREFERRED,
                    value="Customer Service",
                ),
                ExtractedRequirement(
                    category=RequirementCategory.SKILL,
                    importance=RequirementImportance.REQUIRED,
                    value="customer service",
                ),
            ]
        )
    )

    service = RequirementsExtractionService(extractor)

    result = service.extract(create_job())

    assert len(result.requirements) == 1
    assert (
        result.requirements[0].importance
        == RequirementImportance.REQUIRED
    )


def test_service_preserves_extracted_metadata() -> None:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements(
            minimum_experience_months=36,
            entry_level=False,
            work_authorization_required=True,
            sponsorship_available=False,
        )
    )

    service = RequirementsExtractionService(extractor)

    result = service.extract(create_job())

    assert result.minimum_experience_months == 36
    assert result.entry_level is False
    assert result.work_authorization_required is True
    assert result.sponsorship_available is False

def test_metadata_reports_uncached_extraction() -> None:
    extractor = StubRequirementsExtractor(
        ExtractedJobRequirements()
    )

    service = RequirementsExtractionService(
        extractor
    )

    result = service.extract_with_metadata(
        create_job()
    )

    assert result.requirements == JobRequirements()
    assert result.cache_hit is False