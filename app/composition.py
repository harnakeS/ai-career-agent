from app.database.database import SessionLocal
from app.job_sources.collection import (
    CompanyJobCollectionService,
)
from app.job_sources.greenhouse import GreenhouseJobSource
from app.job_sources.models import JobSourceProvider
from app.job_sources.registry import JobSourceRegistry
from app.pipeline.selected_company_pipeline import (
    SelectedCompanyPipeline,
)
from app.config.ai import (
    AIConfiguration,
    AIConfigurationError,
    AIProvider,
)
from app.llm.ollama_client import (
    OllamaStructuredLLMClient,
)
from app.llm.openai_client import (
    OpenAIStructuredLLMClient,
)
from app.matching.service import (
    CandidateJobMatchService,
)
from app.parsing.requirements.llm_extractor import (
    LLMRequirementsExtractor,
)
from app.parsing.requirements.service import (
    RequirementsExtractionService,
)
from app.matching.evidence_matcher import EvidenceMatcher
from app.matching.normalizer import RequirementNormalizer
from app.vocabulary.defaults import (
    create_default_vocabulary_repository,
)


def create_selected_company_pipeline(
) -> SelectedCompanyPipeline:
    """
    Construct the selected-company pipeline with production dependencies.

    This composition function is shared by command-line and frontend
    entry points.
    """

    registry = JobSourceRegistry(
        sources={
            JobSourceProvider.GREENHOUSE: (
                GreenhouseJobSource()
            ),
        }
    )

    collection_service = CompanyJobCollectionService(
        registry=registry
    )

    return SelectedCompanyPipeline(
        collection_service=collection_service,
        session_factory=SessionLocal,
    )

def create_candidate_job_match_service(
    configuration: AIConfiguration,
) -> CandidateJobMatchService:
    """Construct candidate-to-job matching with the configured AI provider."""

    if configuration.provider == AIProvider.DISABLED:
        raise AIConfigurationError(
            "AI requirement extraction is disabled. "
            "Configure AI_PROVIDER before matching jobs."
        )

    if configuration.model is None:
        raise AIConfigurationError(
            "An AI model is required for job matching."
        )

    if configuration.provider == AIProvider.OPENAI:
        if configuration.openai_api_key is None:
            raise AIConfigurationError(
                "OPENAI_API_KEY is required for "
                "OpenAI job matching."
            )

        client = OpenAIStructuredLLMClient(
            model=configuration.model,
            api_key=(
                configuration.openai_api_key
                .get_secret_value()
            ),
        )

    elif configuration.provider == AIProvider.OLLAMA:
        client = OllamaStructuredLLMClient(
            model=configuration.model,
            host=configuration.ollama_host,
            timeout_seconds=(
                configuration.ollama_timeout_seconds
            ),
        )

    else:
        raise AIConfigurationError(
            f"Unsupported AI provider: "
            f"{configuration.provider}"
        )

    extractor = LLMRequirementsExtractor(
        client=client
    )

    requirements_service = (
        RequirementsExtractionService(
            extractor=extractor
        )
    )

    vocabulary = create_default_vocabulary_repository()

    normalizer = RequirementNormalizer(
        vocabulary=vocabulary
    )

    evidence_matcher = EvidenceMatcher(
        normalizer=normalizer
    )

    return CandidateJobMatchService(
        requirements_service=requirements_service,
        evidence_matcher=evidence_matcher,
    )