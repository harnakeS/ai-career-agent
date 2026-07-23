from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from app.composition import (
    create_candidate_job_match_service,
)
from app.config.ai import (
    AIConfiguration,
    AIConfigurationError,
    AIProvider,
)
from app.matching.service import (
    CandidateJobMatchService,
)


def test_rejects_disabled_ai_configuration() -> None:
    configuration = AIConfiguration(
        provider=AIProvider.DISABLED
    )

    with pytest.raises(
        AIConfigurationError,
        match="disabled",
    ):
        create_candidate_job_match_service(
            configuration
        )


@patch(
    "app.composition."
    "OpenAIStructuredLLMClient"
)
def test_creates_openai_job_match_service(
    mock_client_class: MagicMock,
) -> None:
    configuration = AIConfiguration(
        provider=AIProvider.OPENAI,
        model="test-openai-model",
        openai_api_key=SecretStr(
            "test-api-key"
        ),
    )

    result = create_candidate_job_match_service(
        configuration
    )

    assert isinstance(
        result,
        CandidateJobMatchService,
    )

    mock_client_class.assert_called_once_with(
        model="test-openai-model",
        api_key="test-api-key",
    )


@patch(
    "app.composition."
    "OllamaStructuredLLMClient"
)
def test_creates_ollama_job_match_service(
    mock_client_class: MagicMock,
) -> None:
    configuration = AIConfiguration(
        provider=AIProvider.OLLAMA,
        model="test-ollama-model",
        ollama_host=(
            "http://example-host:11434"
        ),
    )

    result = create_candidate_job_match_service(
        configuration
    )

    assert isinstance(
        result,
        CandidateJobMatchService,
    )

    mock_client_class.assert_called_once_with(
        model="test-ollama-model",
        host="http://example-host:11434",
        timeout_seconds=90.0,
    )