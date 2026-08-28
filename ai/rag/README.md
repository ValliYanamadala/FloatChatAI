# RAG Placeholder

This directory will contain the future semantic retrieval pipeline for FloatChatAI.

Planned RAG knowledge sources:

- ARGO concepts.
- ARGO parameter definitions.
- Database schema documentation.
- Geographic and ocean-region terminology.
- Query examples.
- Data interpretation guidance.

Raw measurement rows must not be placed into the vector database. Structured numerical data belongs in PostgreSQL/PostGIS and should be accessed through validated MCP/backend tools.

Planned modules:

- `document_ingestion.py`: load curated documents for indexing.
- `chunking.py`: split documents into retrievable chunks.
- `embeddings.py`: create embeddings for approved knowledge documents.
- `vector_store.py`: manage ChromaDB collections.
- `retrieval.py`: retrieve context for intent extraction, planning, and explanation.
