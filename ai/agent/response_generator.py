"""Response generation service producing scientific explanations and visualization specs."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import JsonValue, ValidationError

from ai.llm import LLMProvider
from ai.schemas.contracts import (
    AIResponse,
    AIResponseError,
    Intent,
    MCPToolName,
    OceanParameter,
    QueryPlan,
    VisualizationSpec,
    VisualizationType,
)

LOGGER = logging.getLogger(__name__)
PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


class ResponseGenerator:
    """
    Synthesizes natural-language scientific explanations and structured
    VisualizationSpecs from real MCP/backend data and RAG context.
    """

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        *,
        prompt_dir: Path | None = None,
        temperature: float = 0.0,
    ) -> None:
        self._llm_provider = llm_provider
        self._prompt_dir = prompt_dir or PROMPT_DIR
        self._temperature = temperature

    async def generate(
        self,
        question: str,
        *,
        query_plan: QueryPlan | None = None,
        structured_data: Any = None,
        rag_context: str | None = None,
        intent: Intent | None = None,
        sources: list[str] | None = None,
        warnings: list[str] | None = None,
        errors: list[AIResponseError] | None = None,
    ) -> AIResponse:
        """
        Produce a grounded AIResponse with natural-language text and a VisualizationSpec.
        """
        normalized_question = question.strip()
        accumulated_sources = list(sources or [])
        accumulated_warnings = list(warnings or [])
        accumulated_errors = list(errors or [])

        # Check for error in structured data from backend
        if isinstance(structured_data, dict) and "detail" in structured_data and not structured_data.get("results"):
            error_msg = str(structured_data["detail"])
            accumulated_errors.append(AIResponseError(code="BACKEND_ERROR", message=error_msg))
            return AIResponse(
                answer=f"Could not retrieve ARGO data: {error_msg}",
                intent=intent,
                query_plan=query_plan,
                structured_data=structured_data,
                visualization=None,
                sources=accumulated_sources,
                warnings=accumulated_warnings,
                errors=accumulated_errors,
            )

        # 1. Try LLM Provider if available
        if self._llm_provider is not None:
            try:
                system_prompt = self._load_prompt()
                context_payload: dict[str, JsonValue] = {
                    "question": normalized_question,
                    "query_plan": query_plan.model_dump(mode="json") if query_plan else None,
                    "intent": intent.model_dump(mode="json") if intent else None,
                    "structured_data": structured_data if isinstance(structured_data, (dict, list, str, int, float, bool)) else None,
                    "rag_context": rag_context,
                }
                raw_output = await self._llm_provider.generate_structured(
                    system_prompt=system_prompt,
                    user_message=normalized_question,
                    context=context_payload,
                    output_schema=AIResponse,
                    temperature=self._temperature,
                )
                parsed = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
                if isinstance(parsed, dict) and "answer" in parsed and parsed["answer"]:
                    response = AIResponse.model_validate(parsed)
                    # Ensure original plan and data are attached
                    return AIResponse(
                        answer=response.answer,
                        intent=intent or response.intent,
                        query_plan=query_plan or response.query_plan,
                        structured_data=structured_data or response.structured_data,
                        visualization=response.visualization or self._build_deterministic_visualization(query_plan, structured_data),
                        sources=accumulated_sources or response.sources,
                        warnings=accumulated_warnings or response.warnings,
                        errors=accumulated_errors or response.errors,
                    )
            except Exception as exc:
                LOGGER.info("response_generator.llm_fallback", extra={"reason": str(exc)})

        # 2. Deterministic Grounded Synthesis (Offline / Mock fallback)
        return self._generate_deterministic(
            question=normalized_question,
            query_plan=query_plan,
            structured_data=structured_data,
            rag_context=rag_context,
            intent=intent,
            sources=accumulated_sources,
            warnings=accumulated_warnings,
            errors=accumulated_errors,
        )

    def _load_prompt(self) -> str:
        prompt_file = self._prompt_dir / "response_generation.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8").strip()
        return "You are the FloatChatAI response-generation layer. Summarize ARGO data accurately."

    def _generate_deterministic(
        self,
        question: str,
        query_plan: QueryPlan | None,
        structured_data: Any,
        rag_context: str | None,
        intent: Intent | None,
        sources: list[str],
        warnings: list[str],
        errors: list[AIResponseError],
    ) -> AIResponse:
        """Deterministic scientific explanation without external API calls."""

        # Conceptual knowledge question without query plan
        if query_plan is None:
            if rag_context:
                answer = (
                    f"Based on FloatChatAI oceanographic knowledge:\n\n{rag_context.strip()}"
                )
            else:
                answer = f"No specific ARGO data query was executed for: '{question}'."
            return AIResponse(
                answer=answer,
                intent=intent,
                query_plan=None,
                structured_data=structured_data,
                visualization=None,
                sources=sources,
                warnings=warnings,
                errors=errors,
            )

        tool = query_plan.tool
        data = structured_data or {}
        visualization = self._build_deterministic_visualization(query_plan, data)

        # Tool-specific grounded scientific text generation
        if tool == MCPToolName.NEAREST_FLOATS:
            answer = self._synthesize_nearest_floats(data, query_plan.arguments)

        elif tool == MCPToolName.SEARCH_FLOATS:
            answer = self._synthesize_search_floats(data, query_plan.arguments)

        elif tool == MCPToolName.GET_PROFILE:
            answer = self._synthesize_get_profile(data, query_plan.arguments)

        elif tool == MCPToolName.GET_TRAJECTORY:
            answer = self._synthesize_get_trajectory(data, query_plan.arguments)

        elif tool == MCPToolName.QUERY_MEASUREMENTS:
            answer = self._synthesize_query_measurements(data, query_plan.arguments)

        elif tool == MCPToolName.GET_STATISTICS:
            answer = self._synthesize_get_statistics(data, query_plan.arguments)

        elif tool == MCPToolName.GET_FLOAT_METADATA:
            answer = self._synthesize_float_metadata(data, query_plan.arguments)

        else:
            answer = f"Query executed successfully via {tool.value}."

        return AIResponse(
            answer=answer,
            intent=intent,
            query_plan=query_plan,
            structured_data=structured_data,
            visualization=visualization,
            sources=sources,
            warnings=warnings,
            errors=errors,
        )

    # -------------------------------------------------------------------------
    # Scientific Text Synthesizers (Grounded exclusively in returned data)
    # -------------------------------------------------------------------------

    def _synthesize_nearest_floats(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        results = data.get("results") or []
        total_found = data.get("total_found", len(results))
        q_point = data.get("query_point", {})
        lat = q_point.get("latitude", arguments.get("latitude"))
        lon = q_point.get("longitude", arguments.get("longitude"))
        radius_km = data.get("search_radius_km", arguments.get("radius_km", 500))

        loc_str = f"{lat}°N, {lon}°E" if (lat is not None and lon is not None) else "the target coordinates"

        if total_found == 0 or not results:
            return f"No ARGO floats were found within {radius_km:.0f} km of {loc_str}."

        if total_found == 1:
            first = results[0]
            f_id = first.get("float_id", "Unknown")
            dist = first.get("distance_km", 0.0)
            f_lat = first.get("latitude")
            f_lon = first.get("longitude")
            date_str = f" (reported on {first['last_reported_at']})" if first.get("last_reported_at") else ""
            coord_str = f" at ({f_lat:.2f}°, {f_lon:.2f}°)" if (f_lat is not None and f_lon is not None) else ""
            return (
                f"One ARGO float was found within {radius_km:.0f} km of {loc_str}. "
                f"{f_id} is approximately {dist:.1f} km away{coord_str}{date_str}."
            )

        top_floats = ", ".join(f"{r.get('float_id')} ({r.get('distance_km', 0):.1f} km)" for r in results[:3])
        return (
            f"Found {total_found} ARGO floats within {radius_km:.0f} km of {loc_str}. "
            f"Nearest floats include: {top_floats}."
        )

    def _synthesize_search_floats(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        items = data.get("items") or []
        total = data.get("total", len(items))
        region = arguments.get("region")
        plat = arguments.get("platform_number")

        filter_desc = f"in region '{region}'" if region else (f"with platform #{plat}" if plat else "matching criteria")

        if total == 0 or not items:
            return f"No ARGO floats were found {filter_desc}."

        float_ids = [item.get("id") for item in items[:5] if item.get("id")]
        id_summary = ", ".join(float_ids)
        if total > 5:
            id_summary += f", and {total - 5} more"

        return f"Found {total} ARGO floats {filter_desc}: {id_summary}."

    def _synthesize_get_profile(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        if not data or "id" not in data:
            return f"Profile #{arguments.get('profile_id')} was not found."

        p_id = data.get("id")
        f_id = data.get("float_id")
        cycle = data.get("cycle_number", p_id)
        date_val = data.get("timestamp") or data.get("date")
        lat = data.get("latitude")
        lon = data.get("longitude")
        slices = data.get("measurements") or data.get("levels") or []

        slice_info = f" with {len(slices)} depth levels" if slices else ""
        date_info = f" on {str(date_val)[:10]}" if date_val else ""
        loc_info = f" at ({lat:.2f}°, {lon:.2f}°)" if (lat is not None and lon is not None) else ""

        return f"Retrieved profile #{p_id} for float {f_id} (cycle {cycle}){loc_info}{date_info}{slice_info}."

    def _synthesize_get_trajectory(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        f_id = data.get("float_id", arguments.get("float_id"))
        traj = data.get("trajectory") or data.get("points") or []

        if not traj:
            return f"No trajectory points recorded for float {f_id}."

        return f"Retrieved {len(traj)} trajectory fixes for ARGO float {f_id}."

    def _synthesize_query_measurements(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        items = data.get("items") or (data if isinstance(data, list) else [])
        total = data.get("total", len(items))

        if total == 0 or not items:
            return "No oceanographic measurements matched the requested query parameters."

        param = arguments.get("parameter") or "oceanographic parameters"
        return f"Retrieved {total} measurement records for {param}."

    def _synthesize_get_statistics(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        if not data:
            return "No statistical summary available for the specified criteria."

        total_floats = data.get("total_floats", 0)
        params = data.get("parameters") or []
        region = arguments.get("region") or data.get("region", "global dataset")

        if params and isinstance(params, list):
            p_summaries = []
            for p in params:
                name = p.get("name", "parameter")
                mean_val = p.get("mean")
                min_val = p.get("min")
                max_val = p.get("max")
                if mean_val is not None:
                    p_summaries.append(f"{name}: mean={mean_val:.2f} (min={min_val:.2f}, max={max_val:.2f})")
            p_text = "; ".join(p_summaries)
            return f"Oceanographic statistics for {region} ({total_floats} floats): {p_text}."

        return f"Summary statistics computed across {total_floats} floats in {region}."

    def _synthesize_float_metadata(self, data: dict[str, Any], arguments: dict[str, Any]) -> str:
        if not data or "id" not in data:
            return f"Metadata for float '{arguments.get('float_id')}' was not found."

        f_id = data.get("id")
        region = data.get("region") or (data.get("metadata", {}).get("region") if isinstance(data.get("metadata"), dict) else None)
        profiles_count = data.get("total_profiles", data.get("profile_count", 0))
        region_str = f" in the {region}" if region else ""

        return f"Float {f_id}{region_str} has {profiles_count} recorded profile cycles."

    # -------------------------------------------------------------------------
    # Visualization Specification Builder
    # -------------------------------------------------------------------------

    def _build_deterministic_visualization(
        self, query_plan: QueryPlan | None, data: Any
    ) -> VisualizationSpec | None:
        """Construct frontend-independent VisualizationSpec based on tool & data."""
        if not query_plan:
            return None

        # Check if plan already has an explicit valid visualization spec
        if query_plan.visualization:
            return query_plan.visualization

        tool = query_plan.tool
        args = query_plan.arguments or {}

        if tool == MCPToolName.NEAREST_FLOATS:
            lat = args.get("latitude")
            lon = args.get("longitude")
            radius_km = args.get("radius_km", 500)
            return VisualizationSpec(
                type=VisualizationType.MAP,
                title=f"Nearest ARGO Floats to ({lat}, {lon})",
                latitude_field="latitude",
                longitude_field="longitude",
                data_reference="nearest_floats",
                options={
                    "query_point": {"latitude": lat, "longitude": lon},
                    "radius_km": radius_km,
                    "highlight_nearest": True,
                },
            )

        if tool == MCPToolName.SEARCH_FLOATS:
            region = args.get("region", "Global")
            return VisualizationSpec(
                type=VisualizationType.MAP,
                title=f"ARGO Floats — {region}",
                latitude_field="last_location.latitude",
                longitude_field="last_location.longitude",
                data_reference="floats",
                options={"cluster": True},
            )

        if tool == MCPToolName.GET_PROFILE:
            p_id = args.get("profile_id")
            return VisualizationSpec(
                type=VisualizationType.PROFILE_CHART,
                title=f"Vertical Ocean Profile #{p_id}",
                variables=[OceanParameter.TEMPERATURE, OceanParameter.SALINITY],
                x_axis="temperature",
                y_axis="pressure",
                depth_field="pressure_dbar",
                units={"temperature": "°C", "salinity": "PSU", "pressure": "dbar"},
                data_reference="profile",
            )

        if tool == MCPToolName.GET_TRAJECTORY:
            f_id = args.get("float_id", "ARGO")
            return VisualizationSpec(
                type=VisualizationType.TRAJECTORY_MAP,
                title=f"Drift Trajectory — Float {f_id}",
                latitude_field="latitude",
                longitude_field="longitude",
                time_field="timestamp",
                data_reference="trajectory",
                options={"show_path": True, "show_cycle_markers": True},
            )

        if tool == MCPToolName.QUERY_MEASUREMENTS:
            param = args.get("parameter", "temperature")
            return VisualizationSpec(
                type=VisualizationType.PROFILE_CHART,
                title=f"Depth Profile — {param}",
                x_axis=str(param),
                y_axis="pressure",
                depth_field="pressure_dbar",
                data_reference="measurements",
            )

        if tool == MCPToolName.GET_STATISTICS:
            region = args.get("region", "Region")
            return VisualizationSpec(
                type=VisualizationType.STATISTICS,
                title=f"Oceanographic Parameter Summary — {region}",
                data_reference="statistics",
                options={"chart_type": "bar"},
            )

        if tool == MCPToolName.GET_FLOAT_METADATA:
            f_id = args.get("float_id", "ARGO")
            return VisualizationSpec(
                type=VisualizationType.TABLE,
                title=f"Float Specifications & History — {f_id}",
                data_reference="metadata",
            )

        return None
