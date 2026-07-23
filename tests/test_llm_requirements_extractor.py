from typing import Any

from pydantic import BaseModel

from app.models.job import JobPosting
from app.models.job_requirements import (
    RequirementCategory,
    RequirementImportance,
)
from app.parsing.requirements.llm_extractor import (
    LLMRequirementsExtractor,
    SYSTEM_PROMPT,
    build_user_prompt,
)
from app.parsing.requirements.schema import (
    ExtractedJobRequirements,
    ExtractedRequirement,
)


class RecordingStructuredLLMClient:
    def __init__(
        self,
        result: ExtractedJobRequirements,
    ) -> None:
        self._result = result
        self.system_prompt: str | None = None
        self.user_prompt: str | None = None
        self.response_model: type[BaseModel] | None = None

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[Any],
    ) -> Any:
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.response_model = response_model

        return self._result


def create_job() -> JobPosting:
    return JobPosting(
        source="test",
        external_id="job-123",
        requisition_id="REQ-123",
        company="Example Hospital",
        title="Registered Nurse",
        location="Newark, NJ",
        description=(
            "An active RN license is required. "
            "BLS certification is preferred."
        ),
        application_url="https://example.com/jobs/job-123",
    )


def test_build_user_prompt_includes_job_information() -> None:
    prompt = build_user_prompt(create_job())

    assert "Registered Nurse" in prompt
    assert "Example Hospital" in prompt
    assert "Newark, NJ" in prompt
    assert "active RN license is required" in prompt


def test_system_prompt_does_not_limit_extraction_to_tech_jobs() -> None:
    assert "any profession or industry" in SYSTEM_PROMPT
    assert "predefined vocabulary" in SYSTEM_PROMPT
    assert "Do not evaluate the candidate" in SYSTEM_PROMPT


def test_llm_extractor_requests_structured_job_requirements() -> None:
    expected = ExtractedJobRequirements(
        requirements=[
            ExtractedRequirement(
                category=RequirementCategory.CERTIFICATION,
                importance=RequirementImportance.REQUIRED,
                value="Active RN License",
                source_text="An active RN license is required.",
            )
        ]
    )
    client = RecordingStructuredLLMClient(expected)
    extractor = LLMRequirementsExtractor(client)

    result = extractor.extract(create_job())

    assert result == expected
    assert client.system_prompt == SYSTEM_PROMPT
    assert client.response_model is ExtractedJobRequirements


def test_llm_extractor_sends_job_description_to_client() -> None:
    client = RecordingStructuredLLMClient(
        ExtractedJobRequirements()
    )
    extractor = LLMRequirementsExtractor(client)

    extractor.extract(create_job())

    assert client.user_prompt is not None
    assert "Registered Nurse" in client.user_prompt
    assert "active RN license is required" in client.user_prompt

def test_system_prompt_requires_atomic_requirement_values() -> None:
    assert "concise, atomic value" in SYSTEM_PROMPT
    assert "separate independent qualifications" in SYSTEM_PROMPT


def test_system_prompt_distinguishes_and_from_or() -> None:
    assert "Python or SQL" in SYSTEM_PROMPT
    assert "Python and SQL" in SYSTEM_PROMPT
    assert "alternatives" in SYSTEM_PROMPT

def test_system_prompt_separates_duration_from_domain() -> None:
    assert "At least 24 months" in SYSTEM_PROMPT
    assert "Corporate Finance" in SYSTEM_PROMPT
    assert "Data Analytics" in SYSTEM_PROMPT
    assert "two experience requirements" in SYSTEM_PROMPT


def test_system_prompt_separates_competency_from_tools() -> None:
    assert (
        "Experience in data analytics using SQL, Python, or R"
        in SYSTEM_PROMPT
    )
    assert "two requirements" in SYSTEM_PROMPT
    assert "category: experience" in SYSTEM_PROMPT
    assert "category: skill" in SYSTEM_PROMPT

def test_build_user_prompt_uses_qualification_sections() -> None:
    job = JobPosting(
        source="test",
        external_id="job-456",
        requisition_id="REQ-456",
        company="Example Company",
        title="Data Analyst",
        location="New York, NY",
        description="""
**What You’ll Do:**

- Build reports for management.

**Who You Are:**

- Experience using SQL or Python.
- Bachelor's degree in computer science.

**Benefits:**

- Health insurance.
""".strip(),
        application_url=(
            "https://example.com/jobs/job-456"
        ),
    )

    prompt = build_user_prompt(job)

    assert "Experience using SQL or Python" in prompt
    assert "Bachelor's degree" in prompt
    assert "Build reports for management" not in prompt
    assert "Health insurance" not in prompt