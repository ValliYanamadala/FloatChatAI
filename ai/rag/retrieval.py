"""Retrieval service for FloatChatAI RAG knowledge chunks."""

from __future__ import annotations

from ai.rag.embeddings import EmbeddingProvider
from ai.rag.types import RetrievalResult
from ai.rag.vector_store import VectorStore


class RAGRetriever:
    """Retrieve relevant trusted knowledge without accessing measurements."""

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        min_score: float = 0.1,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.min_score = min_score

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        query_embedding = self.embedding_provider.embed_query(query)
        results = self.vector_store.similarity_search(
            query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )
        return [result for result in results if result.score >= self.min_score]
