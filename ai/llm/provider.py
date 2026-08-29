"""Provider-independent LLM interface for structured output generation."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, JsonValue


class LLMProvider(Protocol):
    """Minimal interface implemented by any structured-output LLM provider."""

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_message: str,
        context: dict[str, JsonValue] | None = None,
        output_schema: type[BaseModel] | None = None,
        temperature: float = 0.0,
    ) -> JsonValue | str:
        """Return structured JSON-compatible output for a user message."""
