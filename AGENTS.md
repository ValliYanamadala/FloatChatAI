# AGENTS.md

## Project Purpose

FloatChatAI is an AI-powered conversational interface for exploring and visualizing ARGO oceanographic data for SIH 2026. Users should be able to ask natural-language ocean-data questions and receive validated data queries, visualizations, and grounded explanations.

## Architecture Principles

- PostgreSQL with PostGIS is the source of truth for structured float, profile, trajectory, and measurement data.
- ChromaDB is planned as the semantic knowledge store for RAG content such as ARGO concepts, parameter definitions, schema documentation, ocean-region terminology, query examples, and interpretation guidance.
- The LLM is responsible for reasoning, intent extraction, planning, and explanation. It is not the source of numerical truth.
- The LLM must not execute unrestricted AI-generated SQL. It should produce validated structured requests that flow through MCP/backend tools.
- MCP is the controlled tool interface between the AI layer and data/backend capabilities.
- Do not invent missing ARGO schema details or data semantics. Preserve the normalized target schema unless a task explicitly changes it.

## Component Responsibilities

- `frontend/`: React + TypeScript user interface for chat, maps, charts, and structured results.
- `backend/`: Python + FastAPI application layer for authenticated APIs, validation, orchestration, and database access.
- `data/`: Python/xarray data-processing workspace for raw data, processed artifacts, and ETL scripts.
- `ai/`: Prompts, schemas, RAG scaffolding, LLM adapters, and agent orchestration.
- `mcp/`: Future MCP server and tool definitions for controlled access to data capabilities.
- `tests/`: Unit and contract tests for meaningful logic.
- `docs/`: Architecture, setup, and workstream documentation.
- `docker/`: Container and deployment support files.

## Development Rules

- Keep changes focused and avoid unnecessary rewrites of working code.
- Maintain backward compatibility with defined AI/MCP contracts.
- Add tests for meaningful logic, especially validation and cross-component contracts.
- Keep secrets out of source control. Use `.env.example` for placeholders only.
- Generated datasets and local caches should not be committed.
- Prefer typed, validated interfaces over free-form dictionaries when crossing component boundaries.
