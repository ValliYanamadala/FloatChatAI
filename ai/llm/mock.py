"""Deterministic LLM provider for tests and local development."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy

from pydantic import BaseModel, JsonValue


MockResponse = JsonValue | str


class MockLLMProvider:
    """Return configured responses without API calls or network access."""

    def __init__(
        self,
        responses: Mapping[str, MockResponse] | Sequence[MockResponse] | None = None,
        *,
        default_response: MockResponse | None = None,
    ) -> None:
        self._responses = responses if responses is not None else {}
        self._default_response = default_response
        self.calls: list[dict[str, object]] = []
        self._sequence_index = 0

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_message: str,
        context: dict[str, JsonValue] | None = None,
        output_schema: type[BaseModel] | None = None,
        temperature: float = 0.0,
    ) -> MockResponse:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_message": user_message,
                "context": deepcopy(context),
                "output_schema": output_schema,
                "temperature": temperature,
            }
        )

        if isinstance(self._responses, Mapping):
            if user_message in self._responses:
                return deepcopy(self._responses[user_message])
            if self._default_response is not None:
                return deepcopy(self._default_response)
            raise KeyError(f"No mock LLM response configured for: {user_message}")

        if self._sequence_index < len(self._responses):
            response = self._responses[self._sequence_index]
            self._sequence_index += 1
            return deepcopy(response)

        if self._default_response is not None:
            return deepcopy(self._default_response)

        raise IndexError("No mock LLM responses remaining")
