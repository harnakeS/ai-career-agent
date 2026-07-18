from app.models.job import JobPosting
from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.extractor import (
    RequirementsExtractor,
    StubRequirementsExtractor,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)


def create_job() -> JobPosting:
    return JobPosting(
        source="test",
        external_id="job-123",
        requisition_id="REQ-123",
        company="Example Company",
        title="Backend Engineer",
        location="New York, NY",
        description="Python and SQL experience required.",
        application_url="https://example.com/jobs/job-123",
    )


def test_stub_requirements_extractor_returns_configured_result() -> None:
    expected = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.SKILL,
                importance=RequirementImportance.REQUIRED,
                value="Python",
                source_text="Python experience required.",
            )
        ]
    )

    extractor = StubRequirementsExtractor(expected)

    result = extractor.extract(create_job())

    assert result == expected


def test_stub_satisfies_requirements_extractor_protocol() -> None:
    expected = ExtractedJobRequirements()
    extractor: RequirementsExtractor = StubRequirementsExtractor(expected)

    result = extractor.extract(create_job())

    assert result == expected


def test_stub_returns_same_validated_result_for_multiple_jobs() -> None:
    expected = ExtractedJobRequirements(
        minimum_experience_months=12,
        entry_level=True,
    )
    extractor = StubRequirementsExtractor(expected)

    first_result = extractor.extract(create_job())
    second_result = extractor.extract(create_job())

    assert first_result == expected
    assert second_result == expected