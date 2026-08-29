import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch
import pytest
import requests

from ai.schemas.contracts import MCPToolName, QueryPlan
from app.adapters.query_plan_adapter import QueryPlanAdapter
import mcp.server as mcp_module
from mcp.server import (
    get_backend_url,
    get_float_metadata,
    get_profile,
    get_statistics,
    get_trajectory,
    mcp,
    nearest_floats,
    query_measurements,
    search_floats,
)


class MCPServerUnitTests(unittest.TestCase):
    """Deterministic automated unit tests for FloatChatAI FastMCP server and tools."""

    def test_mcp_server_initialization_and_tool_count(self):
        """Verify MCP server instance and registered tool count."""
        self.assertEqual(mcp.name, "FloatChatAI")
        tools = asyncio.run(mcp.list_tools())
        self.assertEqual(len(tools), 7)

    def test_mcp_all_7_tools_registered_with_schemas(self):
        """Verify all 7 MCP tools are discoverable and expose input schemas."""
        tools = asyncio.run(mcp.list_tools())
        tool_names = {t.name for t in tools}
        expected_tools = {
            "search_floats",
            "nearest_floats",
            "get_profile",
            "get_trajectory",
            "query_measurements",
            "get_statistics",
            "get_float_metadata",
        }
        self.assertEqual(tool_names, expected_tools)

        for t in tools:
            self.assertIsNotNone(t.description)
            self.assertIn("properties", t.inputSchema)

    def test_mcp_backend_url_configuration(self):
        """Verify FLOATCHAT_BACKEND_URL environment variable configuration."""
        with patch.dict(os.environ, {"FLOATCHAT_BACKEND_URL": "http://backend-service:8080/"}):
            self.assertEqual(get_backend_url(), "http://backend-service:8080")

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_backend_url(), "http://localhost:8000")

    @patch("requests.get")
    def test_search_floats_tool(self, mock_get):
        """Verify search_floats tool calls GET /api/v1/floats with parameters."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total": 1, "items": [{"id": "ARGO_001", "region": "North Atlantic"}]}
        mock_get.return_value = mock_resp

        result = search_floats(region="North Atlantic", limit=20, offset=0)
        self.assertEqual(result["total"], 1)
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/floats",
            params={"region": "North Atlantic", "limit": 20, "offset": 0},
            timeout=10,
        )

    @patch("requests.post")
    def test_nearest_floats_tool(self, mock_post):
        """Verify nearest_floats tool calls POST /api/v1/nearest-floats with payload."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total_found": 1, "results": [{"float_id": "ARGO_001", "distance_km": 12.5}]}
        mock_post.return_value = mock_resp

        result = nearest_floats(latitude=42.0, longitude=-42.0, radius_km=300.0, limit=5)
        self.assertEqual(result["total_found"], 1)
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/nearest-floats",
            json={
                "latitude": 42.0,
                "longitude": -42.0,
                "radius_km": 300.0,
                "max_distance_km": 300.0,
                "limit": 5,
            },
            timeout=10,
        )

    @patch("requests.get")
    def test_get_profile_tool(self, mock_get):
        """Verify get_profile tool calls GET /api/v1/profiles/{id}."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": 42, "float_id": "ARGO_001"}
        mock_get.return_value = mock_resp

        result = get_profile(profile_id=42)
        self.assertEqual(result["id"], 42)
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/profiles/42",
            params=None,
            timeout=10,
        )

    @patch("requests.get")
    def test_get_trajectory_tool(self, mock_get):
        """Verify get_trajectory tool calls GET /api/v1/floats/{id}/trajectory."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"float_id": "ARGO_001", "trajectory": []}
        mock_get.return_value = mock_resp

        result = get_trajectory(float_id="ARGO_001")
        self.assertEqual(result["float_id"], "ARGO_001")
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/floats/ARGO_001/trajectory",
            params=None,
            timeout=10,
        )

    @patch("requests.get")
    def test_query_measurements_tool(self, mock_get):
        """Verify query_measurements tool calls GET /api/v1/measurements."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total": 5, "items": []}
        mock_get.return_value = mock_resp

        result = query_measurements(float_id="ARGO_001", min_depth=10.0, max_depth=100.0)
        self.assertEqual(result["total"], 5)
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/measurements",
            params={"float_id": "ARGO_001", "min_depth": 10.0, "max_depth": 100.0, "limit": 100, "offset": 0},
            timeout=10,
        )

    @patch("requests.get")
    def test_get_statistics_tool(self, mock_get):
        """Verify get_statistics tool calls GET /api/v1/statistics."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total_floats": 20, "parameters": []}
        mock_get.return_value = mock_resp

        result = get_statistics(region="Arabian Sea")
        self.assertEqual(result["total_floats"], 20)
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/statistics",
            params={"region": "Arabian Sea"},
            timeout=10,
        )

    @patch("requests.get")
    def test_get_float_metadata_tool(self, mock_get):
        """Verify get_float_metadata tool calls GET /api/v1/floats/{id}."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "ARGO_005", "region": "Indian Ocean"}
        mock_get.return_value = mock_resp

        result = get_float_metadata(float_id="ARGO_005")
        self.assertEqual(result["id"], "ARGO_005")
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/floats/ARGO_005",
            params=None,
            timeout=10,
        )

    @patch("requests.get")
    def test_backend_http_error_handling(self, mock_get):
        """Verify HTTP errors from backend raise HTTPError safely."""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_resp

        with self.assertRaises(requests.exceptions.HTTPError):
            get_profile(profile_id=99999)

    @patch("requests.get")
    def test_sql_injection_string_safety(self, mock_get):
        """Verify SQL injection strings are safely passed as parameterized parameters."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total": 0, "items": []}
        mock_get.return_value = mock_resp

        malicious_input = "ARGO_001'; DROP TABLE profiles;--"
        search_floats(platform_number=malicious_input)
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/floats",
            params={"platform_number": malicious_input, "limit": 100, "offset": 0},
            timeout=10,
        )


class MCPQueryPlanIntegrationTests(unittest.TestCase):
    """Test AI QueryPlan to MCP tool execution flow."""

    @patch("requests.get")
    def test_query_plan_dispatches_to_mcp_get_trajectory(self, mock_get):
        """Verify QueryPlan with GET_TRAJECTORY executes through MCP tool handler."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"float_id": "ARGO_001", "trajectory": [{"lat": 42.0, "lon": -42.0}]}
        mock_get.return_value = mock_resp

        plan = QueryPlan(
            tool=MCPToolName.GET_TRAJECTORY,
            arguments={"float_id": "ARGO_001"},
        )
        result = QueryPlanAdapter.execute_via_mcp(plan)
        self.assertEqual(result["float_id"], "ARGO_001")
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/v1/floats/ARGO_001/trajectory",
            params=None,
            timeout=10,
        )

    @patch("requests.post")
    def test_query_plan_dispatches_to_mcp_nearest_floats(self, mock_post):
        """Verify QueryPlan with NEAREST_FLOATS executes through MCP tool handler."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total_found": 2, "results": []}
        mock_post.return_value = mock_resp

        plan = QueryPlan(
            tool=MCPToolName.NEAREST_FLOATS,
            arguments={
                "location": {"latitude": 10.0, "longitude": 60.0, "radius_km": 250},
                "limit": 5,
            },
        )
        result = QueryPlanAdapter.execute_via_mcp(plan)
        self.assertEqual(result["total_found"], 2)
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/v1/nearest-floats",
            json={
                "latitude": 10.0,
                "longitude": 60.0,
                "radius_km": 250,
                "max_distance_km": 250,
                "limit": 5,
            },
            timeout=10,
        )
