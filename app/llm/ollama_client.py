from typing import TypeVar

from ollama import Client
from pydantic import BaseModel

from app.llm.client import StructuredLLMClient


ResponseModelT = TypeVar(
    "ResponseModelT",
    bound=BaseModel,
)


class OllamaStructuredLLMClient(StructuredLLMClient):
    """Local Ollama implementation of the structured LLM client."""

    def __init__(
        self,
        *,
        model: str = "qwen3:4b",
        host: str = "http://localhost:11434",
    ) -> None:
        self._client = Client(host=host)
        self._model = model

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        response = self._client.chat(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=response_model.model_json_schema(),
            options={
                "temperature": 0,
            },
        )

        content = response.message.content

        if not content:
            raise RuntimeError(
                "Ollama returned no structured output."
            )

        return response_model.model_validate_json(content)