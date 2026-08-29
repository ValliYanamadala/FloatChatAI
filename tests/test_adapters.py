import pytest

from ai.schemas.contracts import (
    DateRange,
    DepthRange,
    Intent,
    IntentType,
    Location,
    MCPToolName,
    OceanParameter,
    QueryPlan,
)
from app.adapters.query_plan_adapter import QueryPlanAdapter


def test_query_plan_to_query_request_parameters_and_depth():
    """Verify QueryPlan with parameters and depth interval converts to QueryRequest."""
    plan = QueryPlan(
        tool=MCPToolName.QUERY_MEASUREMENTS,
        arguments={
            "parameters": ["temperature", "salinity"],
            "depth_range_m": {"min_depth_m": 0, "max_depth_m": 150},
            "float_id": "ARGO_001",
        },
    )

    req = QueryPlanAdapter.to_query_request(plan)
    assert req.float_ids == ["ARGO_001"]
    assert req.parameters == ["temperature_C", "salinity"]
    assert req.depth_range == {"min": 0.0, "max": 150.0}


def test_query_plan_to_query_request_location_and_dates():
    """Verify QueryPlan with coordinate radius location converts to bounding box."""
    plan = QueryPlan(
        tool=MCPToolName.QUERY_MEASUREMENTS,
        arguments={
            "location": {"latitude": 42.0, "longitude": -42.0, "radius_km": 200},
            "date_range": {"start_date": "2026-08-01", "end_date": "2026-08-10"},
        },
    )

    req = QueryPlanAdapter.to_query_request(plan)
    assert req.bounding_box is not None
    assert req.bounding_box.min_lat < 42.0 < req.bounding_box.max_lat
    assert req.bounding_box.min_lon < -42.0 < req.bounding_box.max_lon
    assert req.start_date is not None
    assert req.end_date is not None


def test_query_plan_to_nearest_floats_request():
    """Verify QueryPlan with NEAREST_FLOATS converts to NearestFloatsRequest."""
    plan = QueryPlan(
        tool=MCPToolName.NEAREST_FLOATS,
        arguments={
            "location": {"latitude": 15.5, "longitude": 68.2, "radius_km": 500},
            "limit": 10,
        },
    )

    req = QueryPlanAdapter.to_nearest_floats_request(plan)
    assert req.latitude == 15.5
    assert req.longitude == 68.2
    assert req.max_distance_km == 500.0
    assert req.limit == 10
