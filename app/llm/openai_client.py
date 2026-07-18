import os
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app.llm.client import StructuredLLMClient


ResponseModelT = TypeVar(
    "ResponseModelT",
    bound=BaseModel,
)


class OpenAIStructuredLLMClient(StructuredLLMClient):
    """OpenAI implementation of the structured LLM client contract."""

    def __init__(
        self,
        *,
        model: str = "gpt-4.1-mini",
        api_key: str | None = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not resolved_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be provided or set in the environment."
            )

        self._client = OpenAI(api_key=resolved_api_key)
        self._model = model

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        response = self._client.responses.parse(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=response_model,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "OpenAI returned no parsed structured output."
            )

        return parsed