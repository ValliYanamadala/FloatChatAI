import json
import unittest

from ai.agent import LLMResponseParsingError, QueryUnderstandingService, SchemaValidationError
from ai.llm import MockLLMProvider
from ai.schemas import MCPToolName, OceanParameter


def valid_response(**overrides):
    response = {
        "answer": None,
        "intent": {
            "intent_type": "float_search",
            "parameters": [],
            "region": "Arabian Sea",
            "confidence": 0.9,
            "original_question": "Show me ARGO floats in the Arabian Sea.",
        },
        "query_plan": {
            "tool": "search_floats",
            "arguments": {"region": "Arabian Sea"},
            "visualization": {"type": "map"},
        },
        "metadata": {"stage": "query_understanding"},
    }
    response.update(overrides)
    return response


class QueryUnderstandingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_structured_output(self) -> None:
        provider = MockLLMProvider(default_response=valid_response())
        service = QueryUnderstandingService(provider)

        result = await service.understand("Show me ARGO floats in the Arabian Sea.")

        self.assertEqual(result.intent.intent_type.value, "float_search")
        self.assertEqual(result.query_plan.tool, MCPToolName.SEARCH_FLOATS)
        self.assertEqual(provider.calls[0]["temperature"], 0.0)
        self.assertIn("float_search", provider.calls[0]["system_prompt"])

    async def test_malformed_json(self) -> None:
        provider = MockLLMProvider(default_response="{not json")
        service = QueryUnderstandingService(provider)

        with self.assertRaises(LLMResponseParsingError):
            await service.understand("Show floats in the Arabian Sea.")

    async def test_invalid_intent(self) -> None:
        response = valid_response(intent={"intent_type": "invented_intent"})
        provider = MockLLMProvider(default_response=response)
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Invent an intent.")

    async def test_invalid_mcp_tool(self) -> None:
        response = valid_response(query_plan={"tool": "run_sql", "arguments": {"region": "Arabian Sea"}})
        provider = MockLLMProvider(default_response=response)
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Run SQL for floats.")

    async def test_invalid_variable(self) -> None:
        response = valid_response(
            intent={"intent_type": "time_series", "parameters": ["wave_height"]},
            query_plan={
                "tool": "query_measurements",
                "arguments": {"variables": ["wave_height"], "region": "Arabian Sea"},
            },
        )
        provider = MockLLMProvider(default_response=response)
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Show wave height.")

    async def test_missing_required_fields(self) -> None:
        provider = MockLLMProvider(default_response={"query_plan": {"arguments": {"region": "Arabian Sea"}}})
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Show floats in the Arabian Sea.")

    async def test_raw_sql_attempt(self) -> None:
        response = valid_response(
            query_plan={
                "tool": "query_measurements",
                "arguments": {"raw_sql": "SELECT * FROM measurements"},
            }
        )
        provider = MockLLMProvider(default_response=response)
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Write SQL for measurements.")

    async def test_hallucinated_unsupported_parameter_in_arguments(self) -> None:
        response = valid_response(
            intent={"intent_type": "statistics", "parameters": ["temperature"]},
            query_plan={
                "tool": "get_statistics",
                "arguments": {"parameter": "wind_speed", "region": "Arabian Sea"},
            },
        )
        provider = MockLLMProvider(default_response=response)
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Average wind speed?")

    async def test_ambiguous_query_returns_clarification(self) -> None:
        provider = MockLLMProvider(
            default_response={
                "intent": {
                    "intent_type": "comparison",
                    "parameters": ["temperature"],
                    "confidence": 0.62,
                    "original_question": "Compare temperature.",
                },
                "clarification": {
                    "reason": "Comparison targets are missing.",
                    "missing_fields": ["comparison_targets"],
                    "questions": ["Which regions, floats, or time periods should be compared?"],
                    "original_question": "Compare temperature.",
                },
            }
        )
        service = QueryUnderstandingService(provider)

        result = await service.understand("Compare temperature.")

        self.assertIsNone(result.query_plan)
        self.assertEqual(result.clarification.missing_fields, ["comparison_targets"])

    async def test_valid_bgc_query(self) -> None:
        provider = MockLLMProvider(
            default_response=valid_response(
                intent={
                    "intent_type": "time_series",
                    "parameters": ["oxygen"],
                    "region": "Bay of Bengal",
                    "original_question": "Plot dissolved oxygen observations in the Bay of Bengal.",
                },
                query_plan={
                    "tool": "query_measurements",
                    "arguments": {"variables": ["oxygen"], "region": "Bay of Bengal"},
                    "visualization": {"type": "time_series", "variables": ["oxygen"]},
                },
            )
        )
        service = QueryUnderstandingService(provider)

        result = await service.understand("Plot dissolved oxygen observations in the Bay of Bengal.")

        self.assertEqual(result.intent.parameters, [OceanParameter.OXYGEN])
        self.assertEqual(result.query_plan.tool, MCPToolName.QUERY_MEASUREMENTS)

    async def test_valid_date_range(self) -> None:
        provider = MockLLMProvider(
            default_response=valid_response(
                intent={
                    "intent_type": "time_series",
                    "parameters": ["temperature"],
                    "region": "Arabian Sea",
                    "date_range": {"start_date": "2023-01-01", "end_date": "2023-06-30"},
                },
                query_plan={
                    "tool": "query_measurements",
                    "arguments": {
                        "variables": ["temperature"],
                        "region": "Arabian Sea",
                        "start_date": "2023-01-01",
                        "end_date": "2023-06-30",
                    },
                    "visualization": {"type": "time_series", "variables": ["temperature"]},
                },
            )
        )
        service = QueryUnderstandingService(provider)

        result = await service.understand("Show temperature in the Arabian Sea from 2023-01-01 to 2023-06-30.")

        self.assertEqual(result.intent.date_range.start_date.isoformat(), "2023-01-01")
        self.assertEqual(result.intent.date_range.end_date.isoformat(), "2023-06-30")

    async def test_valid_pressure_range(self) -> None:
        provider = MockLLMProvider(
            default_response=valid_response(
                intent={
                    "intent_type": "profile_query",
                    "parameters": ["salinity"],
                    "pressure_range_dbar": {"min_pressure_dbar": 100, "max_pressure_dbar": 500},
                },
                query_plan={
                    "tool": "query_measurements",
                    "arguments": {
                        "variables": ["salinity"],
                        "pressure_range_dbar": {"min_pressure_dbar": 100, "max_pressure_dbar": 500},
                    },
                    "visualization": {"type": "profile_chart", "variables": ["salinity"]},
                },
            )
        )
        service = QueryUnderstandingService(provider)

        result = await service.understand("Give me salinity measurements between 100 and 500 dbar.")

        self.assertEqual(result.intent.pressure_range_dbar.min_pressure_dbar, 100)
        self.assertEqual(result.intent.pressure_range_dbar.max_pressure_dbar, 500)

    async def test_plan_requires_intent(self) -> None:
        provider = MockLLMProvider(
            default_response={
                "query_plan": {
                    "tool": "search_floats",
                    "arguments": {"region": "Arabian Sea"},
                    "visualization": {"type": "map"},
                }
            }
        )
        service = QueryUnderstandingService(provider)

        with self.assertRaises(SchemaValidationError):
            await service.understand("Show floats in the Arabian Sea.")


class NaturalLanguageFixtureTests(unittest.TestCase):
    def test_fixture_has_representative_cases(self) -> None:
        with open("tests/fixtures/natural_language_questions.json", encoding="utf-8") as fixture_file:
            questions = json.load(fixture_file)

        self.assertGreaterEqual(len(questions), 25)
        for item in questions:
            self.assertIn("expected_intent", item)
            self.assertIn("expected_mcp_tool", item)
            self.assertIn("expected_entities", item)
            self.assertIn("clarification_required", item)


if __name__ == "__main__":
    unittest.main()
