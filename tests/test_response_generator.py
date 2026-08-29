"""Automated tests for ResponseGenerator and VisualizationSpec synthesis."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from ai.agent.response_generator import ResponseGenerator
from ai.llm.mock import MockLLMProvider
from ai.schemas.contracts import (
    AIResponse,
    AIResponseError,
    Intent,
    IntentType,
    Location,
    MCPToolName,
    OceanParameter,
    QueryPlan,
    VisualizationSpec,
    VisualizationType,
)


class ResponseGeneratorUnitTests(unittest.TestCase):
    """Unit tests for ResponseGenerator deterministic and LLM-driven generation."""

    def setUp(self):
        self.generator = ResponseGenerator()

    def test_nearest_floats_response_and_map_visualization(self):
        """Test nearest_floats response generation with map VisualizationSpec."""
        plan = QueryPlan(
            tool=MCPToolName.NEAREST_FLOATS,
            arguments={"latitude": 15.0, "longitude": 65.0, "radius_km": 500.0, "limit": 5},
        )
        data = {
            "query_point": {"latitude": 15.0, "longitude": 65.0},
            "search_radius_km": 500.0,
            "total_found": 1,
            "results": [
                {
                    "float_id": "ARGO_010",
                    "latitude": 18.0,
                    "longitude": 62.5,
                    "distance_km": 425.956,
                    "last_reported_at": "2026-08-19",
                }
            ],
        }

        response = asyncio.run(
            self.generator.generate(
                question="What are the nearest ARGO floats to 15°N, 65°E?",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("ARGO_010", response.answer)
        self.assertTrue("426" in response.answer or "425.9" in response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.MAP)
        self.assertEqual(response.visualization.latitude_field, "latitude")
        self.assertEqual(response.visualization.longitude_field, "longitude")
        self.assertEqual(response.visualization.options.get("query_point"), {"latitude": 15.0, "longitude": 65.0})

    def test_nearest_floats_empty_result_prevents_fabrication(self):
        """Verify no floats found produces an explicit no-result answer without fabricated numbers."""
        plan = QueryPlan(
            tool=MCPToolName.NEAREST_FLOATS,
            arguments={"latitude": 0.0, "longitude": 0.0, "radius_km": 100.0},
        )
        data = {"query_point": {"latitude": 0.0, "longitude": 0.0}, "search_radius_km": 100.0, "total_found": 0, "results": []}

        response = asyncio.run(
            self.generator.generate(
                question="Find floats near 0, 0 within 100km",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("No ARGO floats were found within 100 km", response.answer)
        self.assertNotIn("ARGO_0", response.answer)

    def test_search_floats_response_and_visualization(self):
        """Test search_floats response with region query."""
        plan = QueryPlan(
            tool=MCPToolName.SEARCH_FLOATS,
            arguments={"region": "Arabian Sea", "limit": 10},
        )
        data = {
            "total": 2,
            "items": [
                {"id": "ARGO_010", "metadata": {"region": "Arabian Sea"}},
                {"id": "ARGO_012", "metadata": {"region": "Arabian Sea"}},
            ],
        }

        response = asyncio.run(
            self.generator.generate(
                question="Show floats in Arabian Sea",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Found 2 ARGO floats in region 'Arabian Sea'", response.answer)
        self.assertIn("ARGO_010", response.answer)
        self.assertIn("ARGO_012", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.MAP)

    def test_get_profile_response_and_profile_chart_visualization(self):
        """Test get_profile response generation with profile chart VisualizationSpec."""
        plan = QueryPlan(
            tool=MCPToolName.GET_PROFILE,
            arguments={"profile_id": 42},
        )
        data = {
            "id": 42,
            "float_id": "ARGO_001",
            "cycle_number": 5,
            "latitude": 42.5,
            "longitude": -42.0,
            "timestamp": "2026-08-01T00:00:00",
            "measurements": [{"pressure_dbar": 10.0, "temperature_c": 18.2}],
        }

        response = asyncio.run(
            self.generator.generate(
                question="Get profile 42",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Retrieved profile #42 for float ARGO_001 (cycle 5)", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.PROFILE_CHART)
        self.assertEqual(response.visualization.x_axis, "temperature")
        self.assertEqual(response.visualization.y_axis, "pressure")
        self.assertEqual(response.visualization.units.get("temperature"), "°C")

    def test_get_trajectory_response_and_trajectory_map_visualization(self):
        """Test get_trajectory response generation with trajectory map VisualizationSpec."""
        plan = QueryPlan(
            tool=MCPToolName.GET_TRAJECTORY,
            arguments={"float_id": "ARGO_001"},
        )
        data = {
            "float_id": "ARGO_001",
            "trajectory": [
                {"latitude": 42.0, "longitude": -42.0, "timestamp": "2026-08-01"},
                {"latitude": 42.5, "longitude": -41.8, "timestamp": "2026-08-11"},
            ],
        }

        response = asyncio.run(
            self.generator.generate(
                question="Show trajectory for float ARGO_001",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Retrieved 2 trajectory fixes for ARGO float ARGO_001", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.TRAJECTORY_MAP)
        self.assertEqual(response.visualization.latitude_field, "latitude")
        self.assertEqual(response.visualization.longitude_field, "longitude")

    def test_get_statistics_response_and_statistics_visualization(self):
        """Test get_statistics response generation with statistics VisualizationSpec."""
        plan = QueryPlan(
            tool=MCPToolName.GET_STATISTICS,
            arguments={"region": "North Atlantic"},
        )
        data = {
            "total_floats": 2,
            "region": "North Atlantic",
            "parameters": [{"name": "temperature_C", "mean": 18.5, "min": 4.2, "max": 24.1}],
        }

        response = asyncio.run(
            self.generator.generate(
                question="What are the temperature statistics in North Atlantic?",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Oceanographic statistics for North Atlantic (2 floats)", response.answer)
        self.assertIn("mean=18.50", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.STATISTICS)

    def test_get_float_metadata_response_and_table_visualization(self):
        """Test get_float_metadata response generation with table VisualizationSpec."""
        plan = QueryPlan(
            tool=MCPToolName.GET_FLOAT_METADATA,
            arguments={"float_id": "ARGO_005"},
        )
        data = {
            "id": "ARGO_005",
            "region": "North Pacific",
            "total_profiles": 12,
        }

        response = asyncio.run(
            self.generator.generate(
                question="What is the metadata for ARGO_005?",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Float ARGO_005 in the North Pacific has 12 recorded profile cycles", response.answer)
        self.assertIsNotNone(response.visualization)
        self.assertEqual(response.visualization.type, VisualizationType.TABLE)

    def test_backend_error_handling_gracefully(self):
        """Verify backend error detail is safely packaged without crashing."""
        plan = QueryPlan(
            tool=MCPToolName.GET_PROFILE,
            arguments={"profile_id": 99999},
        )
        data = {"detail": "Profile with ID 99999 not found"}

        response = asyncio.run(
            self.generator.generate(
                question="Get profile 99999",
                query_plan=plan,
                structured_data=data,
            )
        )

        self.assertIn("Could not retrieve ARGO data", response.answer)
        self.assertEqual(len(response.errors), 1)
        self.assertEqual(response.errors[0].code, "BACKEND_ERROR")
        self.assertIsNone(response.visualization)

    def test_conceptual_question_uses_rag_context(self):
        """Verify conceptual questions without QueryPlan utilize RAG knowledge context."""
        rag_context = "ARGO floats are autonomous profiling instruments that measure ocean temperature and salinity."

        response = asyncio.run(
            self.generator.generate(
                question="What is an ARGO float?",
                query_plan=None,
                rag_context=rag_context,
                sources=["ARGO Overview: knowledge_base"],
            )
        )

        self.assertIn("Based on FloatChatAI oceanographic knowledge", response.answer)
        self.assertIn("autonomous profiling instruments", response.answer)
        self.assertEqual(response.sources, ["ARGO Overview: knowledge_base"])
        self.assertIsNone(response.visualization)

    def test_llm_provider_success_flow(self):
        """Verify LLM provider structured output is parsed and preserved."""
        mock_output = {
            "answer": "Custom LLM generated scientific answer for nearest floats.",
            "visualization": {
                "type": "map",
                "title": "Custom LLM Map",
                "variables": [],
                "options": {},
            },
        }
        mock_llm = MockLLMProvider(default_response=mock_output)
        generator_with_llm = ResponseGenerator(llm_provider=mock_llm)

        plan = QueryPlan(
            tool=MCPToolName.NEAREST_FLOATS,
            arguments={"latitude": 15.0, "longitude": 65.0},
        )
        response = asyncio.run(
            generator_with_llm.generate(
                question="Find nearest floats",
                query_plan=plan,
                structured_data={"results": []},
            )
        )

        self.assertEqual(response.answer, "Custom LLM generated scientific answer for nearest floats.")
        self.assertEqual(response.visualization.title, "Custom LLM Map")
