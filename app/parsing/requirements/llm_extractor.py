from app.llm.client import StructuredLLMClient
from app.models.job import JobPosting
from app.parsing.requirements.schema import ExtractedJobRequirements


SYSTEM_PROMPT = """
You extract structured requirements from job descriptions.

Return only requirements explicitly stated or strongly implied by the posting.

The system must work for any profession or industry, including but not limited to:
software, healthcare, finance, education, operations, logistics, legal,
construction, manufacturing, retail, and government.

Classify each requirement using the following guidance:

- skill: an ability, competency, tool, technique, or area of knowledge
- education: a degree, diploma, academic field, or educational level
- experience: prior work, industry, role, or task experience
- certification: a credential earned through training or examination
- license: a government-issued or professional license, such as RN,
  driver's license, CPA, or professional engineer license
- schedule: availability requirements such as weekends, nights,
  rotating shifts, on-call work, or specific working hours
- location: geographic, remote, hybrid, relocation, or travel requirements
- language: spoken or written language requirements
- clearance: security clearance requirements
- authorization: work authorization or sponsorship requirements

For each requirement:
- classify its category
- classify its importance as required, preferred, or optional
- preserve the original meaning
- include the supporting source text when available

When a minimum amount of experience is stated, convert it into months and
populate minimum_experience_months. For example:
- 1 year becomes 12
- 2 years becomes 24
- 6 months remains 6

Do not invent requirements.
Do not evaluate the candidate.
Do not calculate a match score.
Do not restrict extracted skills to a predefined vocabulary.
""".strip()


def build_user_prompt(job: JobPosting) -> str:
    return f"""
Job title: {job.title}
Company: {job.company}
Location: {job.location}

Job description:
{job.description}
""".strip()


class LLMRequirementsExtractor:
    """Extracts job requirements through a structured-output LLM client."""

    def __init__(
        self,
        client: StructuredLLMClient,
    ) -> None:
        self._client = client

    def extract(
        self,
        job: JobPosting,
    ) -> ExtractedJobRequirements:
        return self._client.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(job),
            response_model=ExtractedJobRequirements,
        )

    def test_system_prompt_supports_general_requirement_categories() -> None:
        assert "license:" in SYSTEM_PROMPT
        assert "schedule:" in SYSTEM_PROMPT
        assert "minimum_experience_months" in SYSTEM_PROMPT
        assert "predefined vocabulary" in SYSTEM_PROMPT