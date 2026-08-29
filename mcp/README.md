# FloatChatAI — Model Context Protocol (MCP) Server

The **FloatChatAI MCP Server** provides a controlled, secure, and tool-based interface between the AI reasoning layer (`QueryUnderstandingService`) and the oceanographic data API (`FastAPI` backend + `PostgreSQL/PostGIS`).

---

## 🏛️ Architecture Overview

```text
User Question ("Find floats near 42.0 N, -42.0 W within 500 km")
                         │
                         ▼
             QueryUnderstandingService (ai/agent)
                         │
                         ▼
               Validated QueryPlan (ai/schemas)
                         │
                         ▼
             QueryPlanAdapter (app/adapters)
                         │
                         ▼
             FastMCP Server Tools (mcp/server.py)
                         │
                         ▼
             FastAPI Oceanographic Endpoints (app/api/v1)
                         │
                         ▼
             PostgreSQL 16 + PostGIS Spatial Engine
```

---

## 🛠️ The 7 Controlled MCP Tools

| MCP Tool Name | Description | Target Backend Endpoint | Key Arguments |
| :--- | :--- | :--- | :--- |
| **`search_floats`** | Search ARGO floats by region or platform ID | `GET /api/v1/floats` | `region`, `platform_number`, `limit`, `offset` |
| **`nearest_floats`** | Geodesic spatial radius search using PostGIS | `POST /api/v1/nearest-floats` | `latitude`, `longitude`, `radius_km`, `limit` |
| **`get_profile`** | Retrieve single profiling cycle with sensor slices | `GET /api/v1/profiles/{id}` | `profile_id` |
| **`get_trajectory`** | Chronological drift path (lat, lon, cycle) | `GET /api/v1/floats/{id}/trajectory` | `float_id` |
| **`query_measurements`** | Query physical and BGC depth slice measurements | `GET /api/v1/measurements` | `float_id`, `min_depth`, `max_depth`, `parameter`, `start_time`, `end_time` |
| **`get_statistics`** | Compute oceanographic summary statistics | `GET /api/v1/statistics` | `region`, `parameter`, `min_depth`, `max_depth` |
| **`get_float_metadata`** | Metadata and profile count for specific float | `GET /api/v1/floats/{id}` | `float_id` |

---

## 🔒 Security & Guardrails

1. **Zero Raw SQL Execution:** The MCP layer communicates strictly via typed HTTP REST endpoints with parameterized queries. Raw SQL strings cannot reach the database.
2. **Strict Argument Validation:** Tool input parameters are validated against FastMCP schemas and backend Pydantic models.
3. **Decoupled Architecture:** MCP tools never access PostgreSQL directly, ensuring consistent business logic and permission enforcement in the backend.

---

## ⚙️ Configuration

The MCP server connects to the backend using the `FLOATCHAT_BACKEND_URL` environment variable:

```bash
# Default (Local Development)
export FLOATCHAT_BACKEND_URL="http://localhost:8000"

# Docker Environment
export FLOATCHAT_BACKEND_URL="http://backend:8000"
```

Configure in `.env`:
```ini
FLOATCHAT_BACKEND_URL=http://localhost:8000
```

---

## 🚀 Running the MCP Server

### Run with Python:
```bash
python3 mcp/server.py
```

### Inspect with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python3 mcp/server.py
```

---

## 🧪 Testing

Run the automated MCP test suite:
```bash
# Run pytest covering all MCP tools and QueryPlan integration
pytest tests/test_mcp_server.py -v

# Run standard library unittest
python3 -m unittest tests/test_mcp_server.py
```
