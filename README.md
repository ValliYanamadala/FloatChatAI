# FloatChatAI

**One‑line description:** An AI‑powered conversational platform for exploring and analyzing ARGO oceanographic float data.

---

## Project Overview
FloatChatAI enables users to ask natural‑language questions about global ARGO float observations and receive accurate, grounded answers together with visualisations. It bridges a large oceanographic dataset with a language model while keeping the LLM strictly under control via validated query contracts.

---

## Key Features
- **Natural‑language AI chat** for querying ARGO data (Home page).
- **Interactive Explorer** with map visualisation and searchable float list.
- **Float Details** view showing metadata, trajectory map, profile selector and measurement charts.
- **Analytics** for comparing multiple floats, with temperature/salinity charts and depth controls.
- **Query Explanation** page exposing the generated query plan, metadata and visualisation spec.
- **Real‑backend integration** – all data comes from PostgreSQL + PostGIS (no mock data).

---

## How It Works
```
User Query → AI/NLP (ai/agent) → validated QueryPlan (Pydantic) →
FastAPI backend (app/api/v1) → PostgreSQL + PostGIS → data returned →
Frontend visualises answer and optional map/chart.
```
The LLM never executes unrestricted SQL; it only produces a structured request that the backend validates before running.

---

## Technical Architecture
- **Frontend** – Vite + React (TypeScript). Development server runs on `http://localhost:5175`.
- **Backend** – FastAPI (Python 3.11) exposing `/api/v1/*` endpoints.
- **Database** – PostgreSQL 16 with PostGIS for spatial queries; accessed via SQLAlchemy 2.0 async.
- **AI / RAG** – LLM for intent extraction and response generation; ChromaDB stores semantic knowledge (concepts, schema docs, etc.).
- **MCP** – Model Context Protocol provides controlled tool calls between the AI layer and backend.
- **Visualization** – Plotly and Leaflet are used in the React components.

---

## Application Pages / Workflow
| Page | Description |
|------|-------------|
| **Home** (`/`) | Chat interface; submit query, receive answer and optional visualisation. |
| **Explorer** (`/explorer`) | Browse all floats, filter/search, view map markers, navigate to details. |
| **Float Details** (`/float/:id`) | Shows float metadata, trajectory map, profile selector and measurement charts. |
| **Analytics** (`/analytics`) | Compare two or more selected floats with temperature/salinity charts and depth sliders. |
| **Query Explanation** (`/query‑explanation`) | Displays the raw query plan, parameters, region, record counts, and visualisation specification. |

---

## Example Query
```
What are the nearest ARGO floats to 15°N, 65°E?
```
The system returns a natural‑language answer, a list of matching float IDs (e.g., `ARGO_010`), and a map visualising their locations.

---

## Example Analytics Use Case
```
Compare the temperature profiles of two ARGO floats in the North Atlantic and show how temperature changes with depth.
```
The Analytics page renders side‑by‑side temperature depth‑profile charts for the selected floats, with an interactive depth range slider.

---

## Data Source
ARGO float observations are stored in PostgreSQL + PostGIS. The import script `import_argo_data.py` loads the provided Excel demo dataset into the database. Spatial indexes enable fast proximity searches.

---

## Setup & Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/FloatChatAI.git
cd FloatChatAI

# ---------- Backend ----------
# Create virtual environment and install Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL + PostGIS (Docker Compose)
docker compose --profile infra up -d

# Apply migrations and load demo data
alembic upgrade head
python3 import_argo_data.py

# Run FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ---------- Frontend ----------
cd frontend
npm install
# Ensure allowed hosts are set in vite.config.js (already includes localhost and tunnel hostnames)
npm run dev -- --host 0.0.0.0 --port 5175
```
The frontend will be available at `http://localhost:5175`.

---

## Project Structure
```
FloatChatAI/
├─ ai/                # AI prompt handling, RAG, schemas
├─ app/               # FastAPI backend, adapters, services
│   └─ api/v1/        # API endpoints (/query, /floats, …)
├─ data/              # Raw/demo datasets and ETL scripts
├─ docker/            # Docker configurations
├─ docs/              # Additional documentation
├─ frontend/          # React + TypeScript UI
├─ mcp/               # Model Context Protocol server
├─ tests/             # Test suite
├─ import_argo_data.py
├─ requirements.txt
└─ README.md
```

---

## API Overview (important endpoints)
- `POST /api/v1/query` – Accepts `{ "natural_language_prompt": "..." }` and returns `ai_context.answer` and optional visualization.
- `GET /api/v1/floats` – Retrieves all floats with last location, region, and metadata.
- `GET /api/v1/floats/:id` – Float‑specific metadata.
- `GET /api/v1/profiles/:float_id` – Depth‑profile measurements.
- `GET /api/v1/trajectory/:float_id` – Trajectory points for mapping.

---

## 🏆 GitHub Achievement
**YOLO** — You want it? You merge it.

This achievement was earned by merging a pull request without a review. It is shown as a GitHub profile badge.

---

## Future Scope
- Add real‑time data ingestion pipelines for live ARGO feeds.
- Extend analytics to include biogeochemical parameters.
- Deploy the application with HTTPS and CI/CD.
- Provide user authentication and role‑based access.

---

## License
This project is licensed under the MIT License (see `LICENSE` file).
