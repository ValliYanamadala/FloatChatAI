"""Typed errors for the AI query-understanding layer."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from pydantic import JsonValue

from ai.schemas import AIResponseError


@dataclass
class QueryUnderstandingError(Exception):
    """Base error safe for translation into API responses."""

    code: str
    message: str
    details: Mapping[str, JsonValue] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message

    def to_response_error(self) -> AIResponseError:
        return AIResponseError(code=self.code, message=self.message, details=dict(self.details))


class LLMResponseParsingError(QueryUnderstandingError):
    """Raised when the LLM output cannot be parsed as structured JSON."""

    def __init__(self, message: str = "LLM response could not be parsed as JSON") -> None:
        super().__init__(code="llm_response_parsing_failed", message=message)


class SchemaValidationError(QueryUnderstandingError):
    """Raised when parsed LLM output does not match FloatChatAI contracts."""

    def __init__(self, details: Mapping[str, JsonValue] | None = None) -> None:
        super().__init__(
            code="schema_validation_failed",
            message="LLM response failed schema validation",
            details=details or {},
        )


class UnsupportedRequestError(QueryUnderstandingError):
    """Raised when a request cannot be represented with current contracts."""

    def __init__(self, message: str = "Request is unsupported by the current query-understanding contract") -> None:
        super().__init__(code="unsupported_request", message=message)


class ClarificationRequiredError(QueryUnderstandingError):
    """Raised when a caller requires an executable plan but clarification is needed."""

    def __init__(self, details: Mapping[str, JsonValue] | None = None) -> None:
        super().__init__(
            code="clarification_required",
            message="The request needs clarification before a query plan can be created",
            details=details or {},
        )
