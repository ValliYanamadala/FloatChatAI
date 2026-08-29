"""Vector-store abstractions and implementations for RAG knowledge chunks."""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Protocol

from ai.rag.document_ingestion import KnowledgeDocumentError, _looks_like_raw_measurement_row
from ai.rag.types import KnowledgeChunk, RetrievalResult


class VectorStore(Protocol):
    """Small interface for vector database access."""

    def rebuild_collection(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        """Replace the collection with the supplied chunks and embeddings."""

    def add_documents(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        """Add chunks and embeddings to the collection."""

    def similarity_search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        """Return the most similar chunks."""

    def collection_info(self) -> dict[str, int | str]:
        """Return basic collection metadata."""


class InMemoryVectorStore:
    """Deterministic in-memory vector store for tests and local examples."""

    def __init__(self, *, collection_name: str = "floatchatai_knowledge") -> None:
        self.collection_name = collection_name
        self._records: list[tuple[KnowledgeChunk, list[float]]] = []

    def rebuild_collection(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        self._records = []
        self.add_documents(chunks, embeddings)

    def add_documents(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        _validate_chunks_and_embeddings(chunks, embeddings)
        self._records.extend((chunk, embedding) for chunk, embedding in zip(chunks, embeddings, strict=True))

    def similarity_search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        matches: list[RetrievalResult] = []
        for chunk, embedding in self._records:
            if metadata_filter and not _metadata_matches(chunk.metadata, metadata_filter):
                continue
            matches.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    text=chunk.text,
                    score=_cosine_similarity(query_embedding, embedding),
                    metadata=chunk.metadata,
                )
            )
        return sorted(matches, key=lambda result: (-result.score, result.chunk_id))[:top_k]

    def collection_info(self) -> dict[str, int | str]:
        return {"collection_name": self.collection_name, "count": len(self._records), "backend": "memory"}


class ChromaVectorStore:
    """ChromaDB-backed vector store for local persistent RAG collections."""

    def __init__(self, *, path: str | Path | None = None, collection_name: str = "floatchatai_knowledge") -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is required for ChromaVectorStore") from exc

        chroma_path = Path(path or os.environ.get("CHROMA_PATH", "docker/.data/chroma"))
        chroma_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self._client = chromadb.PersistentClient(path=str(chroma_path))
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def rebuild_collection(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        _validate_chunks_and_embeddings(chunks, embeddings)
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(name=self.collection_name)
        if chunks:
            self.add_documents(chunks, embeddings)

    def add_documents(self, chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
        _validate_chunks_and_embeddings(chunks, embeddings)
        if not chunks:
            return
        self._collection.add(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks],
            embeddings=embeddings,
        )

    def similarity_search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if metadata_filter:
            query_args["where"] = metadata_filter
        raw_results = self._collection.query(**query_args)

        ids = raw_results.get("ids", [[]])[0]
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]
        results: list[RetrievalResult] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    text=text,
                    score=max(0.0, 1.0 - float(distance)),
                    metadata=metadata or {},
                )
            )
        return results

    def collection_info(self) -> dict[str, int | str]:
        return {"collection_name": self.collection_name, "count": self._collection.count(), "backend": "chroma"}


def _validate_chunks_and_embeddings(chunks: list[KnowledgeChunk], embeddings: list[list[float]]) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings must have the same length")
    for chunk in chunks:
        _validate_chunk_text(chunk.text)


def _validate_chunk_text(text: str) -> None:
    lowered = text.casefold()
    if "select * from" in lowered or "drop table" in lowered:
        raise KnowledgeDocumentError("RAG chunks must not contain executable SQL")
    for line in text.splitlines():
        if _looks_like_raw_measurement_row(line):
            raise KnowledgeDocumentError("RAG chunks must not contain raw measurement rows")


def _metadata_matches(metadata: dict[str, str], metadata_filter: dict[str, str]) -> bool:
    return all(metadata.get(key) == value for key, value in metadata_filter.items())


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
