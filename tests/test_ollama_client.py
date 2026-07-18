from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from app.llm.ollama_client import OllamaStructuredLLMClient


class ExampleResponse(BaseModel):
    value: str


@patch("app.llm.ollama_client.Client")
def test_ollama_client_requests_structured_output(
    mock_client_class: MagicMock,
) -> None:
    mock_sdk_client = mock_client_class.return_value
    mock_sdk_client.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content='{"value":"structured result"}'
        )
    )

    client = OllamaStructuredLLMClient(
        model="test-model",
    )

    result = client.generate_structured(
        system_prompt="System instructions",
        user_prompt="User content",
        response_model=ExampleResponse,
    )

    assert result == ExampleResponse(
        value="structured result"
    )

    mock_sdk_client.chat.assert_called_once_with(
        model="test-model",
        messages=[
            {
                "role": "system",
                "content": "System instructions",
            },
            {
                "role": "user",
                "content": "User content",
            },
        ],
        format=ExampleResponse.model_json_schema(),
        options={
            "temperature": 0,
        },
    )


@patch("app.llm.ollama_client.Client")
def test_ollama_client_uses_configured_host(
    mock_client_class: MagicMock,
) -> None:
    OllamaStructuredLLMClient(
        host="http://example-host:11434",
    )

    mock_client_class.assert_called_once_with(
        host="http://example-host:11434"
    )


@patch("app.llm.ollama_client.Client")
def test_ollama_client_rejects_empty_output(
    mock_client_class: MagicMock,
) -> None:
    mock_sdk_client = mock_client_class.return_value
    mock_sdk_client.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(content="")
    )

    client = OllamaStructuredLLMClient()

    with pytest.raises(
        RuntimeError,
        match="no structured output",
    ):
        client.generate_structured(
            system_prompt="System instructions",
            user_prompt="User content",
            response_model=ExampleResponse,
        )


@patch("app.llm.ollama_client.Client")
def test_ollama_client_validates_model_output(
    mock_client_class: MagicMock,
) -> None:
    mock_sdk_client = mock_client_class.return_value
    mock_sdk_client.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content='{"unexpected":"value"}'
        )
    )

    client = OllamaStructuredLLMClient()

    with pytest.raises(ValidationError):
        client.generate_structured(
            system_prompt="System instructions",
            user_prompt="User content",
            response_model=ExampleResponse,
        )