"""Build LLM-ready context from retrieved RAG chunks."""

from __future__ import annotations

from ai.rag.types import RetrievalResult


class ContextBuilder:
    """Format retrieved chunks with source metadata and bounded length."""

    def __init__(self, *, max_chunks: int = 5, max_chars: int = 4_000) -> None:
        if max_chunks < 1:
            raise ValueError("max_chunks must be at least 1")
        if max_chars < 200:
            raise ValueError("max_chars must be at least 200")
        self.max_chunks = max_chunks
        self.max_chars = max_chars

    def build(self, results: list[RetrievalResult]) -> str:
        unique_results = self._deduplicate(results)[: self.max_chunks]
        sections: list[str] = ["Retrieved FloatChatAI knowledge. This is supporting context, not measurement truth."]
        used_chars = len(sections[0])

        for index, result in enumerate(unique_results, start=1):
            source = result.metadata.get("source", "unknown source")
            category = result.metadata.get("category", "unknown category")
            topic = result.metadata.get("topic", "unknown topic")
            section = (
                f"\n\n[Source {index}] category={category}; topic={topic}; "
                f"source={source}; score={result.score:.3f}\n{result.text}"
            )
            if used_chars + len(section) > self.max_chars:
                break
            sections.append(section)
            used_chars += len(section)
        return "".join(sections)

    def _deduplicate(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        seen: set[str] = set()
        unique: list[RetrievalResult] = []
        for result in results:
            key = result.text.strip()
            if key in seen:
                continue
            seen.add(key)
            unique.append(result)
        return unique
