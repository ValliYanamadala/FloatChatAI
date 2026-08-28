# FloatChatAI

FloatChatAI is an early-stage SIH 2026 project for conversational exploration and visualization of ARGO oceanographic data.

The planned product flow is: a user asks a natural-language question, the AI extracts intent and entities, relevant context is retrieved through RAG, a structured query plan is produced, MCP/backend tools retrieve authoritative data from PostgreSQL/PostGIS, and the frontend renders visualizations with a grounded AI-generated explanation.

## SIH Problem Context

Oceanographic datasets such as ARGO are scientifically valuable but difficult to explore without domain knowledge, database skills, and visualization tooling. FloatChatAI aims to make ARGO float data easier to query, compare, and interpret through a controlled conversational interface.

## Problem Being Solved

FloatChatAI is intended to help users ask questions such as:

- Show ARGO floats in a region.
- Find floats nearest to a location.
- Explore temperature, salinity, oxygen, chlorophyll, nitrate, pressure, and pH patterns.
- View profiles, trajectories, time series, comparisons, statistics, and metadata.

The LLM will not be treated as a numerical data source and will not execute arbitrary SQL. It will produce validated structured requests routed through MCP/backend tools.

## Current Status

Currently implemented:

- Repository foundation and workstream folders.
- AI contract schemas using Pydantic.
- Placeholder prompts for future AI workflows.
- Placeholder RAG structure and documentation.
- Unit tests and evaluation-question fixtures for schema validation.

Planned:

- React + TypeScript frontend.
- FastAPI backend.
- PostgreSQL + PostGIS database integration.
- ChromaDB-backed RAG pipeline.
- MCP server and MCP tools.
- ARGO NetCDF ingestion and normalized database loading.
- Chatbot, maps, charts, and scientific result explanations.

Future work:

- Implement backend services, database models, and migrations.
- Implement data ingestion from real ARGO sources.
- Implement RAG ingestion, embeddings, vector storage, and retrieval.
- Implement LLM adapters, agent orchestration, and prompt evaluation.
- Implement MCP tools for controlled data access.
- Build frontend chat and visualization experiences.

## Planned Architecture

```text
User question
  -> AI intent extraction
  -> RAG/context retrieval
  -> structured query plan
  -> MCP tool contract
  -> FastAPI backend
  -> PostgreSQL + PostGIS
  -> ARGO data result
  -> visualization + AI explanation
```

## Technology Stack

- Frontend: React, TypeScript
- Backend: Python, FastAPI
- Data pipeline: Python, xarray
- Structured database: PostgreSQL, PostGIS
- Semantic store: ChromaDB
- AI layer: Pydantic contracts, prompts, future LLM/RAG orchestration
- Tool interface: MCP
- Testing: Python standard-library `unittest`
- Containers: Docker, Docker Compose

## Repository Structure

```text
FloatChatAI/
├── frontend/
├── backend/
├── data/
│   ├── raw/
│   ├── processed/
│   └── scripts/
├── ai/
│   ├── prompts/
│   ├── rag/
│   ├── schemas/
│   ├── llm/
│   └── agent/
├── mcp/
├── tests/
├── docs/
├── docker/
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
└── docker-compose.yml
```

## Development Prerequisites

- Python 3.11+
- Node.js LTS
- Docker Desktop or compatible Docker runtime
- PostgreSQL/PostGIS client tools, when database development begins

## Basic Local Setup

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests
python3 -m compileall ai tests
```

Future setup will add frontend, backend, database, RAG, and MCP startup commands as those components are implemented.

## Team Workstreams

- Frontend: chat interface, map views, charts, result UX.
- Backend: API design, validation, database access, service orchestration.
- Data: ARGO ingestion, normalization, quality checks, staging outputs.
- AI/RAG: intent extraction, query planning, retrieval, response generation.
- MCP: controlled tool contracts and server implementation.
- DevOps: Docker, environment configuration, deployment documentation.
