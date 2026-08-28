---
category: data_quality
topic: rag_safety_rules
source: RAG implementation requirements
version: 2026-08-foundation
---
# RAG Safety Rules

RAG knowledge is supporting scientific and project context, not measurement truth.

Retrieved documents must not be treated as current observation results.

The LLM must not fabricate values absent from retrieved knowledge or database results.

If retrieval relevance is insufficient, return no context or low-confidence context rather than unrelated information.

Source metadata must remain attached to retrieved knowledge.

Raw measurement rows must never be inserted into the vector database.

The RAG layer must not generate executable database queries.
