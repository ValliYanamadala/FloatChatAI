"""Build the local FloatChatAI RAG knowledge collection."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from ai.rag.chunking import DocumentChunker
from ai.rag.document_ingestion import KNOWLEDGE_DIR, load_knowledge_documents
from ai.rag.embeddings import MockEmbeddingProvider
from ai.rag.vector_store import ChromaVectorStore, InMemoryVectorStore


def build_rag_collection(
    *,
    knowledge_dir: Path = KNOWLEDGE_DIR,
    embedding_provider_name: str = "mock",
    store_backend: str = "chroma",
    chroma_path: str | Path | None = None,
    collection_name: str = "floatchatai_knowledge",
) -> dict[str, int | str]:
    documents = load_knowledge_documents(knowledge_dir)
    chunks = DocumentChunker().chunk_documents(documents)
    embedding_provider = _create_embedding_provider(embedding_provider_name)
    embeddings = embedding_provider.embed_documents([chunk.text for chunk in chunks])
    vector_store = _create_vector_store(store_backend, chroma_path=chroma_path, collection_name=collection_name)
    vector_store.rebuild_collection(chunks, embeddings)
    info = vector_store.collection_info()
    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "embedding_provider": embedding_provider_name,
        "store_backend": str(info["backend"]),
        "collection_name": str(info["collection_name"]),
        "collection_count": int(info["count"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the FloatChatAI RAG knowledge collection.")
    parser.add_argument("--knowledge-dir", default=str(KNOWLEDGE_DIR))
    parser.add_argument("--embedding-provider", default=os.environ.get("EMBEDDING_PROVIDER", "mock"))
    parser.add_argument("--store", choices=["chroma", "memory"], default=os.environ.get("RAG_VECTOR_STORE", "chroma"))
    parser.add_argument("--chroma-path", default=os.environ.get("CHROMA_PATH", "docker/.data/chroma"))
    parser.add_argument("--collection-name", default=os.environ.get("RAG_COLLECTION_NAME", "floatchatai_knowledge"))
    args = parser.parse_args()

    report = build_rag_collection(
        knowledge_dir=Path(args.knowledge_dir),
        embedding_provider_name=args.embedding_provider,
        store_backend=args.store,
        chroma_path=args.chroma_path,
        collection_name=args.collection_name,
    )
    for key, value in report.items():
        print(f"{key}: {value}")


def _create_embedding_provider(name: str) -> MockEmbeddingProvider:
    if name == "mock":
        return MockEmbeddingProvider()
    raise RuntimeError(f"Embedding provider '{name}' is not configured. Use EMBEDDING_PROVIDER=mock for local tests.")


def _create_vector_store(
    backend: str,
    *,
    chroma_path: str | Path | None,
    collection_name: str,
) -> InMemoryVectorStore | ChromaVectorStore:
    if backend == "memory":
        return InMemoryVectorStore(collection_name=collection_name)
    if backend == "chroma":
        return ChromaVectorStore(path=chroma_path, collection_name=collection_name)
    raise RuntimeError(f"Unsupported vector store backend: {backend}")


if __name__ == "__main__":
    main()
