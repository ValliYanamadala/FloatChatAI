# FloatChatAI — Frontend Application

React + Vite frontend for FloatChatAI conversational ocean intelligence.

---

## 🏛️ Application Pages & Features

1. **Home (`/`)**: Hero overview, live metric badges, and interactive analysis terminal with suggested ocean queries.
2. **Explorer (`/explorer`)**: Interactive Leaflet map with ARGO float markers, multi-criteria filters (region, parameters, depth slider, status), and multi-float selection for comparison.
3. **Float Details (`/float-details`, `/float/:id`)**: Trajectory drift map, vertical temperature & salinity profile charts, and sensor measurements table with JSON export download.
4. **Comparative Analytics (`/analytics`)**: Side-by-side comparison charts (Temperature vs Depth and surface temperature over time) with parameter selection and AI insight cards.
5. **Query Explanation (`/query-explanation`)**: Transparency pipeline visualizing natural language semantic interpretation, data scope, and processing steps.

---

## 🛠️ Development Setup

```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Run production build
npm run build
```
