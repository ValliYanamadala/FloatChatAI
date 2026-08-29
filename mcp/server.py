import os
import sys
from typing import Any, Dict, Optional
import requests

# Enable submodule resolution for site-packages 'mcp.server.*' (fastmcp, auth, session)
__path__ = [
    os.path.join(_p, "mcp", "server")
    for _p in sys.path
    if "site-packages" in _p and os.path.isdir(os.path.join(_p, "mcp", "server"))
]

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FloatChatAI")


def get_backend_url() -> str:
    """Return configured backend URL with fallback to localhost."""
    return os.getenv("FLOATCHAT_BACKEND_URL", "http://localhost:8000").rstrip("/")


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> dict:
    """Call a GET endpoint in the FastAPI backend."""
    base_url = get_backend_url()
    response = requests.get(
        f"{base_url}{endpoint}",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def api_post(endpoint: str, data: Dict[str, Any]) -> dict:
    """Call a POST endpoint in the FastAPI backend."""
    base_url = get_backend_url()
    response = requests.post(
        f"{base_url}{endpoint}",
        json=data,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def search_floats(
    region: str | None = None,
    platform_number: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Search for ARGO floats using region or platform number."""
    params = {
        "region": region,
        "platform_number": platform_number,
        "limit": limit,
        "offset": offset,
    }
    params = {
        key: value
        for key, value in params.items()
        if value is not None
    }
    return api_get("/api/v1/floats", params)


@mcp.tool()
def nearest_floats(
    latitude: float,
    longitude: float,
    radius_km: float = 100,
    limit: int = 10,
) -> dict:
    """Find ARGO floats near a geographic location."""
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "radius_km": radius_km,
        "max_distance_km": radius_km,
        "limit": limit,
    }
    return api_post("/api/v1/nearest-floats", data)


@mcp.tool()
def get_profile(profile_id: int) -> dict:
    """Get a complete ARGO profile by profile ID."""
    return api_get(f"/api/v1/profiles/{profile_id}")


@mcp.tool()
def get_trajectory(float_id: str) -> dict:
    """Get the trajectory of an ARGO float."""
    return api_get(f"/api/v1/floats/{float_id}/trajectory")


@mcp.tool()
def query_measurements(
    float_id: str | None = None,
    profile_id: int | None = None,
    min_depth: float | None = None,
    max_depth: float | None = None,
    min_pressure: float | None = None,
    max_pressure: float | None = None,
    parameter: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Query ARGO measurements using optional filters."""
    params = {
        "float_id": float_id,
        "profile_id": profile_id,
        "min_depth": min_depth,
        "max_depth": max_depth,
        "min_pressure": min_pressure,
        "max_pressure": max_pressure,
        "parameter": parameter,
        "start_time": start_time,
        "end_time": end_time,
        "limit": limit,
        "offset": offset,
    }
    params = {
        key: value
        for key, value in params.items()
        if value is not None
    }
    return api_get("/api/v1/measurements", params)


@mcp.tool()
def get_statistics(
    float_id: str | None = None,
    region: str | None = None,
    parameter: str | None = None,
    min_depth: float | None = None,
    max_depth: float | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    """Get statistics for ARGO measurements."""
    params = {
        "float_id": float_id,
        "region": region,
        "parameter": parameter,
        "min_depth": min_depth,
        "max_depth": max_depth,
        "start_time": start_time,
        "end_time": end_time,
    }
    params = {
        key: value
        for key, value in params.items()
        if value is not None
    }
    return api_get("/api/v1/statistics", params)


@mcp.tool()
def get_float_metadata(float_id: str) -> dict:
    """Get metadata and details for a specific ARGO float."""
    return api_get(f"/api/v1/floats/{float_id}")


if __name__ == "__main__":
    mcp.run()
