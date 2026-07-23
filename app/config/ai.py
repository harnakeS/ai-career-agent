import os
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path

from dotenv import dotenv_values
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    ValidationError,
    model_validator,
)


class AIProvider(StrEnum):
    """Supported structured-requirement AI providers."""

    DISABLED = "disabled"
    OPENAI = "openai"
    OLLAMA = "ollama"


class AIConfigurationError(Exception):
    """Raised when AI configuration is missing or invalid."""


class AIConfiguration(BaseModel):
    """Validated configuration for structured requirement extraction."""

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    provider: AIProvider = AIProvider.DISABLED
    model: str | None = None

    openai_api_key: SecretStr | None = Field(
        default=None,
        repr=False,
    )

    ollama_host: str = (
        "http://localhost:11434"
    )
    
    ollama_timeout_seconds: float = Field(
        default=90.0,
        gt=0,
        le=300,
    )

    @model_validator(mode="after")
    def validate_provider_requirements(
        self,
    ) -> "AIConfiguration":
        if self.provider == AIProvider.DISABLED:
            return self

        if not self.model:
            raise ValueError(
                "An AI model is required when AI is enabled."
            )

        if (
            self.provider == AIProvider.OPENAI
            and self.openai_api_key is None
        ):
            raise ValueError(
                "OPENAI_API_KEY is required when "
                "AI_PROVIDER is openai."
            )

        return self


def load_ai_configuration(
    *,
    environment: Mapping[str, str] | None = None,
    env_file: str | Path | None = None,
) -> AIConfiguration:
    """Load AI configuration from an optional file and environment."""

    values: dict[str, str] = {}

    if env_file is not None:
        file_values = dotenv_values(
            Path(env_file)
        )

        values.update({
            key: value
            for key, value in file_values.items()
            if value is not None
        })

    values.update(
        dict(
            environment
            if environment is not None
            else os.environ
        )
    )

    raw_provider = (
        values.get("AI_PROVIDER", "disabled")
        .strip()
        .casefold()
    )

    try:
        provider = AIProvider(raw_provider)
    except ValueError as exc:
        raise AIConfigurationError(
            "AI_PROVIDER must be one of: "
            "disabled, openai, ollama."
        ) from exc

    default_models = {
        AIProvider.DISABLED: None,
        AIProvider.OPENAI: "gpt-4.1-mini",
        AIProvider.OLLAMA: "qwen3.5:4b",
    }

    configured_model = (
        values.get("AI_MODEL", "").strip()
        or default_models[provider]
    )

    configured_api_key = (
        values.get("OPENAI_API_KEY", "").strip()
        or None
    )

    configured_ollama_host = (
        values.get(
            "OLLAMA_HOST",
            "http://localhost:11434",
        ).strip()
        or "http://localhost:11434"
    )

    configured_ollama_timeout = (
        values.get(
            "OLLAMA_TIMEOUT_SECONDS",
            "90",
        ).strip()
        or "90"
    )

    try:
        return AIConfiguration(
            provider=provider,
            model=configured_model,
            openai_api_key=configured_api_key,
            ollama_host=configured_ollama_host,
            ollama_timeout_seconds=(
                configured_ollama_timeout
            ),
        )

    except ValidationError as exc:
        raise AIConfigurationError(
            f"Invalid AI configuration: {exc}"
        ) from exc