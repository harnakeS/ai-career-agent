from app.llm.client import StructuredLLMClient
from app.models.job import JobPosting
from app.parsing.requirements.schema import ExtractedJobRequirements
from app.parsing.requirements.qualification_text import (
    extract_qualification_text,
)


SYSTEM_PROMPT = """
You extract structured requirements from job descriptions.

Return only requirements explicitly stated or strongly implied by the posting.

The input may contain qualification-focused sections extracted from a longer
posting. Process every bullet that states a candidate qualification. A single
bullet may contain multiple independent requirements and must be represented
completely.

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
- use a concise, atomic value rather than a complete sentence
- preserve the complete supporting wording in source_text
- separate independent qualifications into separate requirements
- put interchangeable one-of options in alternatives
- every alternative must have the same category and qualification type
  as the primary value
- never put an additional mandatory qualification in alternatives
- never use alternatives to combine a degree with its field of study
- never use alternatives to combine an experience duration with its domain
- never use alternatives to combine a competency with a required tool

Examples:

"Experience with SQL, Python, or R is required"
becomes one skill requirement:
- value: SQL
- alternatives: Python, R

"Bachelor's degree in finance, accounting, business, economics, or
computer science"
becomes two education requirements:
1. value: Bachelor's degree
2. value: Finance
   alternatives: Accounting, Business, Economics, Computer Science

"At least 24 months of experience in FP&A, corporate finance, investment
banking, or data analytics"
becomes two experience requirements:
1. value: At least 24 months
2. value: FP&A
   alternatives: Corporate Finance, Investment Banking, Data Analytics

"Experience in data analytics using SQL, Python, or R"
becomes two requirements:
1. category: experience
   value: Data Analytics
2. category: skill
   value: SQL
   alternatives: Python, R

The distinction between "or" and "and" is important:

"Python or SQL" becomes one requirement with one alternative.

"Python and SQL" becomes two separate requirements because both are
required.

A requirement may use alternatives only when satisfying any one option
fully satisfies that individual requirement. If the sentence contains
two different kinds of qualifications, create separate requirements
even when they appear in the same sentence.

When a minimum amount of experience is stated, convert it into months and
populate minimum_experience_months. For example:
- 1 year becomes 12
- 2 years becomes 24
- 6 months remains 6

Do not return full responsibility statements, personality descriptions,
or general job duties as skills unless the posting explicitly presents
them as candidate qualifications.

Do not invent requirements.
Do not evaluate the candidate.
Do not calculate a match score.
Do not restrict extracted skills to a predefined vocabulary.
""".strip()

def build_user_prompt(job: JobPosting) -> str:
    qualification_text = extract_qualification_text(
        job.description
    )

    return f"""
Job title: {job.title}
Company: {job.company}
Location: {job.location}

Qualification-focused job description:
{qualification_text}
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