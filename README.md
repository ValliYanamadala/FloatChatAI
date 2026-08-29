# FloatChatAI — ARGO Oceanographic Intelligence Platform

FloatChatAI is an intelligent, conversational, and spatial analytical platform for querying global ARGO oceanographic float data (temperature, salinity, pressure, trajectory drift, and biogeochemical (BGC) parameters).

---

## 🌊 Architecture Overview

```text
User Question ("Show upper 100m temperature and salinity for ARGO_001")
                         │
                         ▼
             QueryUnderstandingService (ai/agent)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
   LLM Provider                    RAG Knowledge Layer (ai/rag)
  (ai/llm/provider)            (ChromaDB + Domain Terms + Data Rules)
        │                                 │
        └────────────────┬────────────────┘
                         ▼
              Validated QueryPlan Contract (ai/schemas)
                         │
                         ▼
             Controlled MCP Tool Layer (mcp/server.py)
                         │
                         ▼
             FastAPI Backend Services (app/api/v1)
                         │
                         ▼
             PostgreSQL 16 + PostGIS Spatial Engine
             (SQLAlchemy 2.0 Async + GeoAlchemy2)
                         │
                         ▼
              Structured Result + Trajectory + BGC Slices
                         │
                         ▼
             Response Generator (ai/agent/response_generator.py)
        ┌────────────────┴────────────────┐
        ▼                                 ▼
  Natural Language Answer          VisualizationSpec (Plotly/Leaflet)
```

---

## 🚀 Key Capabilities

1. **Deterministic & SQL-Safe AI Querying:**
   - The LLM never generates or executes raw SQL. It produces validated Pydantic `QueryPlan` contracts routed to strictly parameterized backend queries.
2. **PostGIS Geodesic Spatial Indexing:**
   - Real-time spatial bounding envelope containment (`ST_Within`, `ST_MakeEnvelope`) and geodesic radius proximity searches (`ST_DWithin`, `ST_Distance`).
3. **Multi-Parameter & BGC Float Profiles:**
   - Physical core measurements (`temperature`, `salinity`, `pressure`, `density`) joined with Biogeochemical sensor data (`dissolved oxygen`, `oxygen saturation`, `chlorophyll-a`, `nitrate`, `pH`, `PAR`).
4. **Controlled FastMCP Server:**
   - Model Context Protocol tools (`search_floats`, `nearest_floats`, `get_profile`, `get_trajectory`, `query_measurements`, `get_statistics`, `get_float_metadata`) interfacing AI directly with data.
5. **Domain-Curated RAG System:**
   - Semantic chunking and retrieval from curated knowledge bases (ocean terminology, ARGO instrumentation, data quality flags).
6. **Grounded Scientific Explanations & Declarative Visualizations:**
   - Output contains strictly grounded observations and typed `VisualizationSpec` objects (`map`, `profile_chart`, `trajectory_map`, `time_series`, `statistics`, `table`).

---

## 📁 Repository Structure

```text
FloatChatAI/
├── ai/                             # Authoritative AI & RAG Subsystem
│   ├── agent/                      # Query understanding, response generation, agent orchestrator
│   ├── llm/                        # Provider-independent LLM abstractions & mock
│   ├── prompts/                    # System prompts for intent, planning, response synthesis
│   ├── rag/                        # RAG ingestion, chunking, embeddings & retriever
│   └── schemas/                    # Pydantic AI contracts (Intent, QueryPlan, VisualizationSpec)
├── app/                            # FastAPI Oceanographic Backend
│   ├── adapters/                   # Bridges translating AI QueryPlan -> Backend / MCP
│   ├── api/v1/endpoints/           # REST & PostGIS endpoints (/query, /floats, /profiles, etc.)
│   ├── core/                       # App settings, DB URIs, structured logging
│   ├── db/                         # SQLAlchemy 2.0 async engine & session management
│   ├── models/                     # Float, Profile, Measurement, BGCMeasurement ORM models
│   ├── schemas/                    # Pydantic request/response validation schemas
│   └── services/ai/                # Offline deterministic parser & query utilities
├── alembic/                        # Database migration scripts (PostGIS DDL, tables, indexes)
├── data/                           # Data directory (raw, processed, scripts, ChromaDB)
├── docker/                         # Docker container configurations
├── docs/                           # Documentation and technical specifications
├── frontend/                       # React + TypeScript frontend application (planned)
├── mcp/                            # Model Context Protocol FastMCP server
├── tests/                          # Unified test suite (AI schemas, RAG, endpoints, MCP, E2E)
├── docker-compose.yml              # PostgreSQL + PostGIS & ChromaDB services
├── import_argo_data.py             # Bulk dataset ingestion ETL pipeline
├── argo_20_global_demo_extended.xlsx # Global demo dataset (20 floats, 120 depth profiles + BGC)
├── requirements.txt                # Unified Python dependencies
└── README.md                       # Project documentation
```

---

## 🛠️ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose

### 2. Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Database & Vector Store
```bash
docker compose --profile infra up -d
```

### 4. Configure Environment
```bash
cp .env.example .env
```

### 5. Apply Migrations & Ingest Dataset
```bash
# Apply PostGIS and table migrations
alembic upgrade head

# Ingest global demo float dataset
python3 import_argo_data.py
```

### 6. Run Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing

Run the complete test suite:

```bash
# Run pytest across all endpoints, AI schemas, RAG, MCP, and E2E pipeline
pytest -v

# Run standard library unittest discover
python3 -m unittest discover -s tests

# Verify compilation
python3 -m compileall ai app mcp tests
```
