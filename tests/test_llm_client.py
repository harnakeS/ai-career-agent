from pydantic import BaseModel

from app.llm.client import StructuredLLMClient


class ExampleResponse(BaseModel):
    value: str


class StubStructuredLLMClient:
    def __init__(
        self,
        result: ExampleResponse,
    ) -> None:
        self._result = result

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ExampleResponse],
    ) -> ExampleResponse:
        return self._result


def test_stub_satisfies_structured_llm_client_protocol() -> None:
    expected = ExampleResponse(value="structured output")

    client: StructuredLLMClient = StubStructuredLLMClient(expected)

    result = client.generate_structured(
        system_prompt="Return structured data.",
        user_prompt="Extract the relevant information.",
        response_model=ExampleResponse,
    )

    assert result == expected


def test_structured_client_receives_response_model() -> None:
    expected = ExampleResponse(value="validated output")
    client = StubStructuredLLMClient(expected)

    result = client.generate_structured(
        system_prompt="System instructions",
        user_prompt="User content",
        response_model=ExampleResponse,
    )

    assert isinstance(result, ExampleResponse)
    assert result.value == "validated output"