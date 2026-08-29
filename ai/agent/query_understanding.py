"""Query-understanding service for turning user questions into AI contracts."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import JsonValue, ValidationError

from ai.agent.errors import LLMResponseParsingError, SchemaValidationError, UnsupportedRequestError
from ai.llm import LLMProvider
from ai.schemas import AIResponse


LOGGER = logging.getLogger(__name__)
PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


class QueryUnderstandingService:
    """Validate provider output into a safe Intent/QueryPlan response."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        *,
        prompt_dir: Path | None = None,
        temperature: float = 0.0,
    ) -> None:
        self._llm_provider = llm_provider
        self._prompt_dir = prompt_dir or PROMPT_DIR
        self._temperature = temperature

    async def understand(
        self,
        question: str,
        *,
        context: dict[str, JsonValue] | None = None,
    ) -> AIResponse:
        """Return a validated AIResponse without executing tools or data access."""

        normalized_question = question.strip()
        if not normalized_question:
            raise UnsupportedRequestError("Question must not be empty")

        LOGGER.info(
            "query_understanding.query_received",
            extra={"event": "query_received", "question_length": len(normalized_question)},
        )

        raw_output = await self._llm_provider.generate_structured(
            system_prompt=self._build_system_prompt(),
            user_message=normalized_question,
            context=context,
            output_schema=AIResponse,
            temperature=self._temperature,
        )
        payload = self._parse_provider_output(raw_output)
        response = self._validate_response(payload)
        self._validate_response_semantics(response)

        if response.intent:
            LOGGER.info(
                "query_understanding.intent_extracted",
                extra={"event": "intent_extracted", "intent_type": response.intent.intent_type.value},
            )
        if response.query_plan:
            LOGGER.info(
                "query_understanding.tool_selected",
                extra={"event": "tool_selected", "tool": response.query_plan.tool.value},
            )
        LOGGER.info("query_understanding.validation_success", extra={"event": "validation_success"})
        return response

    def _build_system_prompt(self) -> str:
        prompt_parts = [
            (self._prompt_dir / "intent_extraction.txt").read_text(encoding="utf-8").strip(),
            (self._prompt_dir / "query_planning.txt").read_text(encoding="utf-8").strip(),
        ]
        return "\n\n".join(prompt_parts)

    def _parse_provider_output(self, raw_output: JsonValue | str) -> dict[str, Any]:
        if isinstance(raw_output, str):
            try:
                parsed = json.loads(raw_output)
            except json.JSONDecodeError as exc:
                LOGGER.info(
                    "query_understanding.validation_failure",
                    extra={"event": "validation_failure", "reason": "json_parse_failed"},
                )
                raise LLMResponseParsingError() from exc
        else:
            parsed = raw_output

        if not isinstance(parsed, dict):
            LOGGER.info(
                "query_understanding.validation_failure",
                extra={"event": "validation_failure", "reason": "non_object_output"},
            )
            raise LLMResponseParsingError("LLM response must be a JSON object")
        return parsed

    def _validate_response(self, payload: dict[str, Any]) -> AIResponse:
        try:
            return AIResponse.model_validate(payload)
        except ValidationError as exc:
            LOGGER.info(
                "query_understanding.validation_failure",
                extra={"event": "validation_failure", "reason": "schema_validation_failed"},
            )
            raise SchemaValidationError(details={"errors": exc.errors(include_url=False, include_context=False)}) from exc

    def _validate_response_semantics(self, response: AIResponse) -> None:
        if response.query_plan and response.clarification:
            raise SchemaValidationError(details={"error": "query_plan and clarification are mutually exclusive"})

        if response.query_plan and response.intent is None:
            raise SchemaValidationError(details={"error": "query_plan requires an intent"})

        if response.query_plan is None and response.clarification is None:
            raise UnsupportedRequestError()
