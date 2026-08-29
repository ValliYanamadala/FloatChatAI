"""LLM provider abstractions for FloatChatAI."""

from ai.llm.mock import MockLLMProvider
from ai.llm.provider import LLMProvider

__all__ = ["LLMProvider", "MockLLMProvider"]
