from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from app.llm.openai_client import OpenAIStructuredLLMClient


class ExampleResponse(BaseModel):
    value: str


@patch("app.llm.openai_client.OpenAI")
def test_openai_client_requests_structured_output(
    mock_openai_class: MagicMock,
) -> None:
    expected = ExampleResponse(value="structured result")

    mock_sdk_client = mock_openai_class.return_value
    mock_sdk_client.responses.parse.return_value = SimpleNamespace(
        output_parsed=expected
    )

    client = OpenAIStructuredLLMClient(
        model="test-model",
        api_key="test-key",
    )

    result = client.generate_structured(
        system_prompt="System instructions",
        user_prompt="User content",
        response_model=ExampleResponse,
    )

    assert result == expected

    mock_sdk_client.responses.parse.assert_called_once_with(
        model="test-model",
        input=[
            {
                "role": "system",
                "content": "System instructions",
            },
            {
                "role": "user",
                "content": "User content",
            },
        ],
        text_format=ExampleResponse,
    )


@patch("app.llm.openai_client.OpenAI")
def test_openai_client_uses_environment_api_key(
    mock_openai_class: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "environment-key")

    OpenAIStructuredLLMClient()

    mock_openai_class.assert_called_once_with(
        api_key="environment-key"
    )


def test_openai_client_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY",
    ):
        OpenAIStructuredLLMClient()


@patch("app.llm.openai_client.OpenAI")
def test_openai_client_rejects_missing_parsed_output(
    mock_openai_class: MagicMock,
) -> None:
    mock_sdk_client = mock_openai_class.return_value
    mock_sdk_client.responses.parse.return_value = SimpleNamespace(
        output_parsed=None
    )

    client = OpenAIStructuredLLMClient(
        api_key="test-key",
    )

    with pytest.raises(
        RuntimeError,
        match="no parsed structured output",
    ):
        client.generate_structured(
            system_prompt="System instructions",
            user_prompt="User content",
            response_model=ExampleResponse,
        )