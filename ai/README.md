# FloatChatAI — AI Architecture & Agent Pipeline

The AI reasoning layer in FloatChatAI translates natural-language oceanographic questions into validated query plans, executes them via Model Context Protocol (MCP) tools against PostgreSQL/PostGIS, and generates grounded scientific explanations accompanied by frontend-agnostic visualization specifications.

---

## 🏛️ End-to-End Execution Flow

```text
User Natural-Language Question
               │
               ▼
   1. Knowledge Retrieval (ai/rag) [Optional Domain Context]
               │
               ▼
   2. Query Understanding (ai/agent/query_understanding.py)
      - Extracts structured Intent (ai/schemas/contracts.py)
      - Builds validated QueryPlan (MCPToolName + Arguments)
      - Prevents SQL generation & validates ocean parameters
               │
               ▼
   3. Controlled MCP Tool Dispatch (app/adapters/query_plan_adapter.py)
      - Routes QueryPlan to mcp/server.py tools
      - Calls FastAPI Backend (/api/v1/ endpoints)
      - Queries PostgreSQL 16 + PostGIS Spatial Engine
               │
               ▼
   4. Structured Result Received (JSON from Backend)
               │
               ▼
   5. Response Generation (ai/agent/response_generator.py)
      - Strictly grounds numerical observations in returned data
      - Never fabricates measurements
      - Produces concise natural-language scientific explanation
      - Builds typed VisualizationSpec (map, profile, trajectory, stats, etc.)
               │
               ▼
   6. Structured AIResponse Envelope (ai/schemas/contracts.py)
      - answer (Natural language text)
      - visualization (VisualizationSpec)
      - structured_data (Raw result)
      - sources, warnings, errors
```

---

## 📊 Visualization Specifications (`VisualizationSpec`)

FloatChatAI outputs declarative, frontend-independent visualization specifications ready for rendering by chart/map libraries (e.g. Leaflet, Plotly, Recharts):

| Visualization Type | Description | Key Specification Fields |
| :--- | :--- | :--- |
| **`map`** | Geographic float and radius search | `latitude_field`, `longitude_field`, `options.query_point`, `options.radius_km` |
| **`profile_chart`** / **`profile`** | Vertical depth/pressure vs parameter | `x_axis`, `y_axis`, `depth_field`, `units` |
| **`trajectory_map`** / **`trajectory`** | Chronological drift path | `latitude_field`, `longitude_field`, `time_field`, `data_reference` |
| **`statistics`** | Oceanographic statistical aggregations | `data_reference`, `title`, `options.chart_type` |
| **`table`** | Tabular float specifications & metadata | `data_reference`, `title` |

---

## 🧪 Testing the AI Pipeline

```bash
# Run response generator unit tests
pytest tests/test_response_generator.py -v

# Run full end-to-end pipeline tests
pytest tests/test_e2e_pipeline.py -v

# Run full project test suite (114+ tests)
pytest -q
```
