# Backend Integration

`backend_service.py` is the handoff layer for the backend or MCP developer. It wraps the existing cleaning and analytics modules and returns plain Python dictionaries/lists that can be sent as JSON.

## Import the service

```python
from backend_service import (
    get_correlation_matrix,
    get_depth_statistics,
    get_float_profile,
    get_overall_statistics,
    get_region_statistics,
    get_validation_report,
)
```

The Excel file is located relative to `backend_service.py`, so API requests do not depend on the current working directory.

## FastAPI example

```python
from fastapi import FastAPI, HTTPException
from backend_service import (
    get_depth_statistics,
    get_float_profile,
    get_validation_report,
)

app = FastAPI(title="FloatChat ARGO Analytics API")

@app.get("/api/validation")
def validation():
    return get_validation_report()

@app.get("/api/statistics/depth")
def depth_statistics():
    return get_depth_statistics()

@app.get("/api/floats/{float_id}/profile")
def float_profile(float_id: str):
    profile = get_float_profile(float_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Float not found")
    return profile
```

## Suggested routes

- `GET /api/validation`
- `GET /api/statistics/overall`
- `GET /api/statistics/depth`
- `GET /api/statistics/region`
- `GET /api/statistics/correlation`
- `GET /api/floats/{float_id}/profile`

For a frontend, call these routes with `fetch()` and use the returned arrays for tables or charts. The glossary and ground-truth JSON files are separate RAG and evaluation inputs.
