"""Embedding provider abstractions for FloatChatAI RAG."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol


TOKEN_PATTERN = re.compile(r"[a-z0-9_]+", re.IGNORECASE)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "can",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "me",
    "of",
    "or",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "with",
}


class EmbeddingProvider(Protocol):
    """Provider-independent interface for document and query embeddings."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed document texts."""

    def embed_query(self, text: str) -> list[float]:
        """Embed one query."""


class MockEmbeddingProvider:
    """Deterministic local embedding provider for tests and development."""

    def __init__(self, *, dimensions: int = 1024) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be at least 8")
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in TOKEN_PATTERN.findall(text.casefold()):
            if token in STOP_WORDS:
                continue
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
