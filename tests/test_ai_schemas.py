import unittest
from datetime import date

from pydantic import ValidationError

from ai.schemas import (
    DateRange,
    DepthRange,
    Intent,
    IntentType,
    Location,
    MCPToolName,
    OceanParameter,
    QueryPlan,
    VisualizationSpec,
    VisualizationType,
)


class IntentSchemaTests(unittest.TestCase):
    def test_valid_intent(self) -> None:
        intent = Intent(
            intent_type=IntentType.FLOAT_SEARCH,
            parameters=[OceanParameter.SALINITY],
            region="Arabian Sea",
            date_range=DateRange(start_date=date(2023, 3, 1), end_date=date(2023, 3, 31)),
            confidence=0.91,
            original_question="Show salinity in the Arabian Sea during March 2023.",
        )

        self.assertEqual(intent.intent_type, IntentType.FLOAT_SEARCH)
        self.assertEqual(intent.parameters, [OceanParameter.SALINITY])

    def test_valid_intent_from_json_values(self) -> None:
        intent = Intent.model_validate(
            {
                "intent_type": "nearest_float",
                "parameters": ["temperature"],
                "location": {"name": "Chennai", "radius_km": 100},
                "confidence": 0.8,
            }
        )

        self.assertEqual(intent.intent_type, IntentType.NEAREST_FLOAT)
        self.assertEqual(intent.parameters, [OceanParameter.TEMPERATURE])

    def test_invalid_intent(self) -> None:
        with self.assertRaises(ValidationError):
            Intent(intent_type="unsupported_intent")

    def test_required_intent_type(self) -> None:
        with self.assertRaises(ValidationError):
            Intent(parameters=[OceanParameter.TEMPERATURE])

    def test_invalid_parameter_value(self) -> None:
        with self.assertRaises(ValidationError):
            Intent(intent_type=IntentType.STATISTICS, parameters=["wave_height"])

    def test_invalid_date_range(self) -> None:
        with self.assertRaises(ValidationError):
            Intent(
                intent_type=IntentType.TIME_SERIES,
                date_range=DateRange(start_date=date(2024, 1, 2), end_date=date(2024, 1, 1)),
            )

    def test_invalid_location_requires_reference(self) -> None:
        with self.assertRaises(ValidationError):
            Location(radius_km=50.0)

    def test_invalid_depth_range(self) -> None:
        with self.assertRaises(ValidationError):
            DepthRange(min_depth_m=500.0, max_depth_m=100.0)


class QueryPlanSchemaTests(unittest.TestCase):
    def test_valid_query_plan(self) -> None:
        plan = QueryPlan(
            tool=MCPToolName.QUERY_MEASUREMENTS,
            arguments={
                "variables": ["salinity"],
                "start_date": "2023-03-01",
                "end_date": "2023-03-31",
                "region": "Arabian Sea",
            },
            visualization=VisualizationSpec(
                type=VisualizationType.PROFILE_CHART,
                variables=[OceanParameter.SALINITY],
            ),
        )

        self.assertEqual(plan.tool, MCPToolName.QUERY_MEASUREMENTS)
        self.assertEqual(plan.visualization.type, VisualizationType.PROFILE_CHART)

    def test_valid_query_plan_from_json_values(self) -> None:
        plan = QueryPlan.model_validate(
            {
                "tool": "nearest_floats",
                "arguments": {"location": "Chennai", "limit": 5},
                "visualization": {"type": "map"},
            }
        )

        self.assertEqual(plan.tool, MCPToolName.NEAREST_FLOATS)
        self.assertEqual(plan.visualization.type, VisualizationType.MAP)

    def test_invalid_mcp_tool(self) -> None:
        with self.assertRaises(ValidationError):
            QueryPlan(
                tool="run_sql",
                arguments={"statement": "temperature by region"},
                visualization=VisualizationSpec(type=VisualizationType.TABLE),
            )

    def test_query_plan_rejects_sql_key(self) -> None:
        with self.assertRaises(ValidationError):
            QueryPlan(
                tool=MCPToolName.QUERY_MEASUREMENTS,
                arguments={"raw_sql": "SELECT * FROM measurements"},
            )

    def test_query_plan_rejects_sql_text(self) -> None:
        with self.assertRaises(ValidationError):
            QueryPlan(
                tool=MCPToolName.QUERY_MEASUREMENTS,
                arguments={"filter": "SELECT temperature FROM measurements"},
            )

    def test_query_plan_rejects_unsupported_variable_argument(self) -> None:
        with self.assertRaises(ValidationError):
            QueryPlan(
                tool=MCPToolName.QUERY_MEASUREMENTS,
                arguments={"variables": ["temperature", "wave_height"]},
            )

    def test_required_query_plan_fields(self) -> None:
        with self.assertRaises(ValidationError):
            QueryPlan(tool=MCPToolName.GET_STATISTICS)


class VisualizationSchemaTests(unittest.TestCase):
    def test_valid_visualization_specification(self) -> None:
        spec = VisualizationSpec(
            type=VisualizationType.TRAJECTORY_MAP,
            title="Float trajectory",
            variables=[OceanParameter.TEMPERATURE],
        )

        self.assertEqual(spec.type, VisualizationType.TRAJECTORY_MAP)

    def test_invalid_visualization_type(self) -> None:
        with self.assertRaises(ValidationError):
            VisualizationSpec(type="heat_globe")

    def test_invalid_visualization_parameter_value(self) -> None:
        with self.assertRaises(ValidationError):
            VisualizationSpec(type=VisualizationType.TIME_SERIES, variables=["waves"])


if __name__ == "__main__":
    unittest.main()
