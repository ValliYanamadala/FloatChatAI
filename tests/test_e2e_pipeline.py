"""End-to-end integration tests for FloatChatAI full pipeline."""

import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch

from ai.agent.orchestrator import FloatChatAgent
from ai.agent.query_understanding import QueryUnderstandingService
from ai.agent.response_generator import ResponseGenerator
from ai.llm.mock import MockLLMProvider
from ai.rag.context import ContextBuilder
from ai.rag.retrieval import RAGRetriever
from ai.schemas.contracts import (
    AIResponse,
    ClarificationRequirement,
    Intent,
    IntentType,
    MCPToolName,
    OceanParameter,
    QueryPlan,
    VisualizationType,
)


class EndToEndPipelineTests(unittest.TestCase):
    """Test full FloatChatAI natural-language query to scientific response pipeline."""

    def test_e2e_nearest_floats_question_flow(self):
        """
        Verify end-to-end flow for:
        'What are the nearest ARGO floats to 15°N, 65°E?'
        -> QueryPlan -> MCP nearest_floats -> ResponseGenerator -> final AIResponse.
        """
        question = "What are the nearest ARGO floats to 15°N, 65°E?"

        # 1. Configure Mock LLM for QueryUnderstanding
        mock_understanding = {
            "intent": {
                "intent_type": "nearest_float",
                "location": {"latitude": 15.0, "longitude": 65.0, "radius_km": 500.0},
            },
            "query_plan": {
                "tool": "nearest_floats",
                "arguments": {"latitude": 15.0, "longitude": 65.0, "radius_km": 500.0, "limit": 5},
            },
        }
        mock_llm = MockLLMProvider(default_response=mock_understanding)
        query_service = QueryUnderstandingService(llm_provider=mock_llm)
        response_generator = ResponseGenerator()
        agent = FloatChatAgent(query_understanding=query_service, response_generator=response_generator)

        # 2. Mock MCP backend response (real PostGIS result for 15N, 65E)
        backend_result = {
            "query_point": {"latitude": 15.0, "longitude": 65.0},
            "search_radius_km": 500.0,
            "total_found": 1,
            "results": [
                {
                    "float_id": "ARGO_010",
                    "latitude": 18.0,
                    "longitude": 62.5,
                    "distance_km": 425.95618514023,
                    "last_reported_at": "2026-08-19",
                    "extra": {},
                }
            ],
        }

        with patch("app.adapters.query_plan_adapter.QueryPlanAdapter.execute_via_mcp", return_value=backend_result):
            response = asyncio.run(agent.answer(question))

        # 3. Verify grounded response and VisualizationSpec
        self.assertIsInstance(response, AIResponse)
        self.assertIsNotNone(response.answer)
        self.assertIn("ARGO_010", response.answer)
        self.assertTrue("426" in response.answer or "425.9" in response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.MAP)
        self.assertEqual(response.visualization.latitude_field, "latitude")
        self.assertEqual(response.visualization.longitude_field, "longitude")
        self.assertEqual(response.structured_data, backend_result)

    def test_e2e_profile_query_flow(self):
        """
        Verify end-to-end flow for:
        'Show temperature profile for profile 1'
        -> QueryPlan -> MCP get_profile -> ResponseGenerator -> final AIResponse.
        """
        question = "Show temperature profile for profile 1"

        mock_understanding = {
            "intent": {
                "intent_type": "profile_query",
                "parameters": ["temperature"],
            },
            "query_plan": {
                "tool": "get_profile",
                "arguments": {"profile_id": 1},
            },
        }
        mock_llm = MockLLMProvider(default_response=mock_understanding)
        query_service = QueryUnderstandingService(llm_provider=mock_llm)
        response_generator = ResponseGenerator()
        agent = FloatChatAgent(query_understanding=query_service, response_generator=response_generator)

        profile_data = {
            "id": 1,
            "float_id": "ARGO_001",
            "cycle_number": 1,
            "latitude": 42.5,
            "longitude": -42.0,
            "timestamp": "2026-08-01T00:00:00",
            "measurements": [
                {"pressure_dbar": 10.0, "temperature_c": 18.2, "salinity": 35.5},
                {"pressure_dbar": 50.0, "temperature_c": 16.1, "salinity": 35.4},
            ],
        }

        with patch("app.adapters.query_plan_adapter.QueryPlanAdapter.execute_via_mcp", return_value=profile_data):
            response = asyncio.run(agent.answer(question))

        self.assertIn("Retrieved profile #1 for float ARGO_001", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.PROFILE_CHART)
        self.assertEqual(response.visualization.x_axis, "temperature")
        self.assertEqual(response.visualization.y_axis, "pressure")

    def test_e2e_trajectory_flow(self):
        """
        Verify end-to-end flow for:
        'Show trajectory of float ARGO_001'
        -> QueryPlan -> MCP get_trajectory -> ResponseGenerator -> final AIResponse.
        """
        question = "Show trajectory of float ARGO_001"

        mock_understanding = {
            "intent": {
                "intent_type": "trajectory",
                "float_id": "ARGO_001",
            },
            "query_plan": {
                "tool": "get_trajectory",
                "arguments": {"float_id": "ARGO_001"},
            },
        }
        mock_llm = MockLLMProvider(default_response=mock_understanding)
        query_service = QueryUnderstandingService(llm_provider=mock_llm)
        response_generator = ResponseGenerator()
        agent = FloatChatAgent(query_understanding=query_service, response_generator=response_generator)

        trajectory_data = {
            "float_id": "ARGO_001",
            "trajectory": [
                {"latitude": 42.0, "longitude": -42.0, "timestamp": "2026-08-01"},
                {"latitude": 42.5, "longitude": -41.8, "timestamp": "2026-08-11"},
            ],
        }

        with patch("app.adapters.query_plan_adapter.QueryPlanAdapter.execute_via_mcp", return_value=trajectory_data):
            response = asyncio.run(agent.answer(question))

        self.assertIn("Retrieved 2 trajectory fixes for ARGO float ARGO_001", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.TRAJECTORY_MAP)

    def test_e2e_clarification_flow_stops_before_tool_execution(self):
        """Verify ambiguous queries return clarification requirements without invoking tools."""
        question = "Compare them"

        mock_understanding = {
            "clarification": {
                "reason": "Missing comparison targets and parameters",
                "missing_fields": ["comparison_targets", "parameters"],
                "questions": ["Which ARGO floats or regions would you like to compare?"],
                "original_question": "Compare them",
            }
        }
        mock_llm = MockLLMProvider(default_response=mock_understanding)
        query_service = QueryUnderstandingService(llm_provider=mock_llm)
        response_generator = ResponseGenerator()
        agent = FloatChatAgent(query_understanding=query_service, response_generator=response_generator)

        with patch("app.adapters.query_plan_adapter.QueryPlanAdapter.execute_via_mcp") as mock_mcp:
            response = asyncio.run(agent.answer(question))

        # Ensure MCP tool was never called
        mock_mcp.assert_not_called()
        self.assertIsNotNone(response.clarification)
        self.assertEqual(response.clarification.reason, "Missing comparison targets and parameters")
        self.assertIsNone(response.query_plan)
