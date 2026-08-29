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
             Adapter / MCP Tool Interface (app/adapters)
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
        Interactive Visualizations & Scientific Explanations
```

---

## 🚀 Key Capabilities

1. **Deterministic & SQL-Safe AI Querying:**
   - The LLM never generates or executes raw SQL. It produces validated Pydantic `QueryPlan` contracts routed to strictly parameterized backend queries.
2. **PostGIS Geodesic Spatial Indexing:**
   - Real-time spatial bounding envelope containment (`ST_Within`, `ST_MakeEnvelope`) and geodesic radius proximity searches (`ST_DWithin`, `ST_Distance`).
3. **Multi-Parameter & BGC Float Profiles:**
   - Physical core measurements (`temperature`, `salinity`, `pressure`, `density`) joined with Biogeochemical sensor data (`dissolved oxygen`, `oxygen saturation`, `chlorophyll-a`, `nitrate`, `pH`, `PAR`).
4. **Domain-Curated RAG System:**
   - Semantic chunking and retrieval from curated knowledge bases (ocean terminology, ARGO instrumentation, data quality flags).
5. **Offline & Fallback Resilience:**
   - Rule-based deterministic semantic parser ensuring 100% functionality even when external AI APIs are offline.

---

## 📁 Repository Structure

```text
FloatChatAI/
├── ai/                             # Authoritative AI & RAG Subsystem
│   ├── agent/                      # Query understanding and intent validation
│   ├── llm/                        # Provider-independent LLM abstractions
│   ├── prompts/                    # System prompts for intent & query planning
│   ├── rag/                        # RAG ingestion, chunking, embeddings & retriever
│   └── schemas/                    # Pydantic AI contracts (Intent, QueryPlan, AIResponse)
├── app/                            # FastAPI Oceanographic Backend
│   ├── adapters/                   # Bridges translating AI QueryPlan -> Backend requests
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
├── mcp/                            # Model Context Protocol tools (planned)
├── tests/                          # Unified test suite (AI schemas, RAG, endpoints, spatial)
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
- Docker & Docker Compose (or local PostgreSQL with PostGIS extension)

### 2. Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Database & Vector Store
```bash
docker-compose up -d
```
*Spins up PostgreSQL with PostGIS on port `5432` and ChromaDB on port `8001`.*

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
- **API Base:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Docs:** `http://localhost:8000/redoc`

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Application & PostGIS database health check |
| `GET` | `/floats` | Paginated list of ARGO floats with profile counts |
| `GET` | `/floats/{id}` | Float metadata by WMO ID |
| `GET` | `/floats/{id}/trajectory` | Chronological float drift trajectory (lat, lon, cycle) |
| `GET` | `/profiles` | Paginated float cycle profiles |
| `GET` | `/profiles/{id}` | Single profile cycle with vertical depth slices |
| `GET` | `/measurements` | Vertical measurements with BGC outer join |
| `GET` | `/statistics` | Global / regional oceanographic summary statistics |
| `POST` | `/nearest-floats` | PostGIS geodesic proximity radius search |
| `POST` | `/query` | Dynamic multi-criteria engine (float IDs, bbox, depth, dates, parameters) |

*All endpoints are also prefixed under `/api/v1` (e.g. `/api/v1/query`).*

---

## 🧪 Testing

Run the complete test suite:

```bash
# Run pytest (all endpoints, health, AI query tests, schemas, RAG)
pytest -v

# Run standard unittest discover
python3 -m unittest discover -s tests

# Verify compilation
python3 -m compileall ai app tests
```
