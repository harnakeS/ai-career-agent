from app.llm.ollama_client import OllamaStructuredLLMClient
from app.models.job import JobPosting
from app.parsing.requirements.llm_extractor import (
    LLMRequirementsExtractor,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
)


def main() -> None:
    job = JobPosting(
        source="manual-test",
        external_id="manual-001",
        requisition_id="MANUAL-001",
        company="Example Hospital",
        title="Registered Nurse",
        location="Newark, NJ",
        description=(
            "Applicants must hold an active New Jersey RN license. "
            "At least one year of acute-care nursing experience is required. "
            "BLS certification is required, and ACLS certification is preferred. "
            "Candidates should demonstrate strong patient communication skills "
            "and be available for occasional weekend shifts."
        ),
        application_url="https://example.com/jobs/manual-001",
    )

    client = OllamaStructuredLLMClient(
    model="qwen3:4b",
)
    extractor = LLMRequirementsExtractor(client)
    service = RequirementsExtractionService(extractor)

    requirements = service.extract(job)

    print(requirements.model_dump_json(indent=2))


if __name__ == "__main__":
    main()