from typing import Protocol, TypeVar

from pydantic import BaseModel


ResponseModelT = TypeVar(
    "ResponseModelT",
    bound=BaseModel,
)


class StructuredLLMClient(Protocol):
    """Contract for requesting validated structured output from an LLM."""

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        ...