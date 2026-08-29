import json
import tempfile
import unittest
from pathlib import Path

from ai.rag import (
    ContextBuilder,
    DocumentChunker,
    InMemoryVectorStore,
    KnowledgeChunk,
    KnowledgeDocumentError,
    MockEmbeddingProvider,
    RAGRetriever,
    RAGUsefulness,
    classify_rag_usefulness,
    load_knowledge_documents,
)
from ai.rag.ingest import build_rag_collection
from ai.rag.vector_store import ChromaVectorStore


class RAGDocumentTests(unittest.TestCase):
    def test_document_loading_and_metadata_preservation(self) -> None:
        documents = load_knowledge_documents()

        self.assertGreaterEqual(len(documents), 6)
        metadata = documents[0].metadata
        self.assertIn("category", metadata)
        self.assertIn("topic", metadata)
        self.assertIn("source", metadata)
        self.assertIn("version", metadata)

    def test_document_loader_rejects_raw_measurement_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "bad.md"
            path.write_text(
                "---\ncategory: test\ntopic: bad\nsource: test\nversion: test\n---\n"
                "# Bad\nARGO_001,10,13.08,80.27,34.5,26.1\n",
                encoding="utf-8",
            )

            with self.assertRaises(KnowledgeDocumentError):
                load_knowledge_documents(root)

    def test_document_loader_rejects_sql_like_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / "bad.md"
            path.write_text(
                "---\ncategory: test\ntopic: bad\nsource: test\nversion: test\n---\n"
                "# Bad\nSELECT * FROM measurements\n",
                encoding="utf-8",
            )

            with self.assertRaises(KnowledgeDocumentError):
                load_knowledge_documents(root)


class RAGChunkingTests(unittest.TestCase):
    def test_chunking_is_deterministic_and_preserves_metadata(self) -> None:
        documents = load_knowledge_documents()
        chunker = DocumentChunker(max_chars=500)

        first = chunker.chunk_documents(documents)
        second = chunker.chunk_documents(documents)

        self.assertEqual([chunk.id for chunk in first], [chunk.id for chunk in second])
        self.assertEqual(first[0].metadata["category"], second[0].metadata["category"])
        self.assertIn("document_id", first[0].metadata)

    def test_chunking_preserves_heading_context(self) -> None:
        documents = load_knowledge_documents()
        chunks = DocumentChunker(max_chars=500).chunk_documents(documents)

        self.assertTrue(any("heading" in chunk.metadata for chunk in chunks))


class EmbeddingAndVectorStoreTests(unittest.TestCase):
    def test_mock_embeddings_are_deterministic(self) -> None:
        provider = MockEmbeddingProvider(dimensions=16)

        self.assertEqual(provider.embed_query("salinity units"), provider.embed_query("salinity units"))
        self.assertEqual(len(provider.embed_query("salinity units")), 16)
        self.assertEqual(provider.embed_documents(["oxygen"])[0], provider.embed_query("oxygen"))

    def test_vector_store_interface_and_similarity_retrieval(self) -> None:
        chunks = DocumentChunker().chunk_documents(load_knowledge_documents())
        provider = MockEmbeddingProvider()
        store = InMemoryVectorStore()
        store.rebuild_collection(chunks, provider.embed_documents([chunk.text for chunk in chunks]))

        results = store.similarity_search(provider.embed_query("salinity units PSU"), top_k=3)

        self.assertEqual(store.collection_info()["count"], len(chunks))
        self.assertGreater(len(results), 0)
        self.assertTrue(any("salinity" in result.text.casefold() for result in results))

    def test_metadata_filtering(self) -> None:
        chunks = DocumentChunker().chunk_documents(load_knowledge_documents())
        provider = MockEmbeddingProvider()
        store = InMemoryVectorStore()
        store.rebuild_collection(chunks, provider.embed_documents([chunk.text for chunk in chunks]))

        results = store.similarity_search(
            provider.embed_query("pressure units"),
            top_k=5,
            metadata_filter={"category": "parameters"},
        )

        self.assertGreater(len(results), 0)
        self.assertTrue(all(result.metadata["category"] == "parameters" for result in results))

    def test_vector_store_rejects_raw_measurement_chunks(self) -> None:
        chunk = KnowledgeChunk(
            id="bad",
            text="ARGO_001,10,13.08,80.27,34.5,26.1",
            metadata={"category": "bad", "topic": "bad", "source": "test", "version": "test"},
        )
        store = InMemoryVectorStore()

        with self.assertRaises(KnowledgeDocumentError):
            store.add_documents([chunk], [[0.1] * 64])

    def test_vector_store_rejects_sql_chunks(self) -> None:
        chunk = KnowledgeChunk(
            id="bad",
            text="SELECT * FROM measurements",
            metadata={"category": "bad", "topic": "bad", "source": "test", "version": "test"},
        )
        store = InMemoryVectorStore()

        with self.assertRaises(KnowledgeDocumentError):
            store.add_documents([chunk], [[0.1] * 64])

    def test_chroma_integration_where_available(self) -> None:
        try:
            import chromadb  # noqa: F401
        except ImportError:
            self.skipTest("chromadb is not installed")

        chunks = DocumentChunker().chunk_documents(load_knowledge_documents())[:2]
        provider = MockEmbeddingProvider()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaVectorStore(path=tmpdir, collection_name="test_floatchatai_knowledge")
            store.rebuild_collection(chunks, provider.embed_documents([chunk.text for chunk in chunks]))
            results = store.similarity_search(provider.embed_query("ARGO float"), top_k=1)

        self.assertEqual(len(results), 1)


class RetrievalAndContextTests(unittest.TestCase):
    def test_retriever_returns_relevant_chunks(self) -> None:
        chunks = DocumentChunker().chunk_documents(load_knowledge_documents())
        provider = MockEmbeddingProvider()
        store = InMemoryVectorStore()
        store.rebuild_collection(chunks, provider.embed_documents([chunk.text for chunk in chunks]))
        retriever = RAGRetriever(embedding_provider=provider, vector_store=store, min_score=0.05)

        results = retriever.retrieve("What does dissolved oxygen mean?", top_k=5)

        self.assertGreater(len(results), 0)
        self.assertTrue(any("oxygen" in result.text.casefold() for result in results))

    def test_low_relevance_retrieval_returns_empty(self) -> None:
        chunks = DocumentChunker().chunk_documents(load_knowledge_documents())
        provider = MockEmbeddingProvider()
        store = InMemoryVectorStore()
        store.rebuild_collection(chunks, provider.embed_documents([chunk.text for chunk in chunks]))
        retriever = RAGRetriever(embedding_provider=provider, vector_store=store, min_score=0.99)

        self.assertEqual(retriever.retrieve("unrelated term with weak overlap", top_k=5), [])

    def test_context_building_preserves_sources_and_deduplicates(self) -> None:
        result = DocumentChunker().chunk_documents(load_knowledge_documents())[0]
        retrieval = {
            "chunk_id": result.id,
            "text": result.text,
            "score": 0.9,
            "metadata": result.metadata,
        }
        from ai.rag.types import RetrievalResult

        context = ContextBuilder(max_chunks=3, max_chars=1200).build(
            [RetrievalResult.model_validate(retrieval), RetrievalResult.model_validate(retrieval)]
        )

        self.assertIn("supporting context, not measurement truth", context)
        self.assertIn("source=", context)
        self.assertEqual(context.count("[Source"), 1)


class RAGRoutingAndIngestionTests(unittest.TestCase):
    def test_routing_classifies_knowledge_questions(self) -> None:
        route = classify_rag_usefulness("What does PSAL mean?")

        self.assertEqual(route.rag_usefulness, RAGUsefulness.USEFUL)
        self.assertFalse(route.database_required)
        self.assertIn("parameters", route.suggested_categories)

    def test_routing_classifies_database_primary_questions(self) -> None:
        route = classify_rag_usefulness("What is the average temperature in the Arabian Sea?")

        self.assertEqual(route.rag_usefulness, RAGUsefulness.NOT_PRIMARY)
        self.assertTrue(route.database_required)

    def test_ingestion_with_mock_memory_store(self) -> None:
        report = build_rag_collection(embedding_provider_name="mock", store_backend="memory")

        self.assertGreaterEqual(report["documents"], 6)
        self.assertGreaterEqual(report["chunks"], report["documents"])
        self.assertEqual(report["embedding_provider"], "mock")
        self.assertEqual(report["store_backend"], "memory")

    def test_rag_evaluation_fixture(self) -> None:
        with open("tests/fixtures/rag_evaluation_questions.json", encoding="utf-8") as fixture_file:
            questions = json.load(fixture_file)

        self.assertGreaterEqual(len(questions), 20)
        for item in questions:
            self.assertIn("expected_rag_usefulness", item)
            self.assertIn("expected_category", item)
            self.assertIn("relevant_topic", item)
            self.assertIn("database_required", item)


if __name__ == "__main__":
    unittest.main()
