from pathlib import Path

import pytest

from app.config.ai import (
    AIConfigurationError,
    AIProvider,
    load_ai_configuration,
)


def test_ai_is_disabled_by_default() -> None:
    configuration = load_ai_configuration(
        environment={}
    )

    assert (
        configuration.provider
        == AIProvider.DISABLED
    )
    assert configuration.model is None
    assert configuration.openai_api_key is None


def test_loads_openai_configuration() -> None:
    configuration = load_ai_configuration(
        environment={
            "AI_PROVIDER": "openai",
            "AI_MODEL": "test-model",
            "OPENAI_API_KEY": "test-key",
        }
    )

    assert (
        configuration.provider
        == AIProvider.OPENAI
    )
    assert configuration.model == "test-model"
    assert configuration.openai_api_key is not None
    assert (
        configuration.openai_api_key.get_secret_value()
        == "test-key"
    )


def test_openai_uses_default_model() -> None:
    configuration = load_ai_configuration(
        environment={
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
        }
    )

    assert configuration.model == "gpt-4.1-mini"


def test_openai_requires_api_key() -> None:
    with pytest.raises(
        AIConfigurationError,
        match="OPENAI_API_KEY",
    ):
        load_ai_configuration(
            environment={
                "AI_PROVIDER": "openai",
            }
        )


def test_loads_ollama_configuration() -> None:
    configuration = load_ai_configuration(
        environment={
            "AI_PROVIDER": "ollama",
            "OLLAMA_HOST": (
                "http://example-host:11434"
            ),
        }
    )

    assert (
        configuration.provider
        == AIProvider.OLLAMA
    )
    assert configuration.model == "qwen3.5:4b"
    assert (
        configuration.ollama_host
        == "http://example-host:11434"
    )
    assert configuration.ollama_timeout_seconds == 90.0


def test_rejects_unknown_ai_provider() -> None:
    with pytest.raises(
        AIConfigurationError,
        match="disabled, openai, ollama",
    ):
        load_ai_configuration(
            environment={
                "AI_PROVIDER": "unknown",
            }
        )


def test_loads_configuration_from_env_file(
    tmp_path: Path,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join([
            "AI_PROVIDER=ollama",
            "AI_MODEL=local-test-model",
            "OLLAMA_HOST=http://localhost:11434",
        ]),
        encoding="utf-8",
    )

    configuration = load_ai_configuration(
        environment={},
        env_file=env_path,
    )

    assert (
        configuration.provider
        == AIProvider.OLLAMA
    )
    assert (
        configuration.model
        == "local-test-model"
    )

def test_loads_custom_ollama_timeout() -> None:
    configuration = load_ai_configuration(
        environment={
            "AI_PROVIDER": "ollama",
            "AI_MODEL": "test-model",
            "OLLAMA_TIMEOUT_SECONDS": "45",
        }
    )

    assert configuration.ollama_timeout_seconds == 45.0


def test_rejects_excessive_ollama_timeout() -> None:
    with pytest.raises(
        AIConfigurationError,
        match="Invalid AI configuration",
    ):
        load_ai_configuration(
            environment={
                "AI_PROVIDER": "ollama",
                "AI_MODEL": "test-model",
                "OLLAMA_TIMEOUT_SECONDS": "600",
            }
        )