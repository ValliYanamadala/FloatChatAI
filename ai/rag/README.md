# RAG Knowledge Layer

This directory contains the first production-oriented RAG knowledge layer for FloatChatAI.

RAG is used for trusted semantic/scientific context such as:

- ARGO concepts.
- ARGO parameter definitions.
- Variable mappings and units.
- Data-quality and interpretation rules.
- Database schema semantics.
- Geographic and ocean-region terminology.
- Representative query examples.

RAG is not the source of truth for numerical measurement results. Structured observations belong in PostgreSQL/PostGIS and will be accessed later through validated MCP/backend tools.

## Components

- `knowledge/`: curated Markdown corpus with required front-matter metadata.
- `document_ingestion.py`: deterministic document loader and safety checks.
- `chunking.py`: deterministic Markdown chunker that preserves metadata and headings.
- `embeddings.py`: provider abstraction and deterministic mock embedding implementation.
- `vector_store.py`: vector-store abstraction, in-memory store, and ChromaDB-backed store.
- `retrieval.py`: `RAGRetriever` for top-k retrieval with metadata filters.
- `context.py`: source-preserving context builder for future LLM prompts.
- `routing.py`: lightweight RAG usefulness classifier.
- `ingest.py`: deterministic collection build command.

## Safety Rules

- Retrieved knowledge is supporting context, not current measurement data.
- Retrieved documents must not be treated as actual observation results.
- The LLM must not fabricate values absent from retrieved knowledge or database results.
- Low-relevance retrieval should return no context instead of unrelated context.
- Source metadata must remain attached to retrieved chunks.
- Raw measurement rows must never be inserted into the vector database.
- The RAG layer must not generate executable database queries.

## Local Ingestion

Use mock embeddings for local deterministic ingestion:

```bash
python3 -m ai.rag.ingest --embedding-provider mock --store chroma
```

For tests or temporary runs:

```bash
python3 -m ai.rag.ingest --embedding-provider mock --store memory
```
