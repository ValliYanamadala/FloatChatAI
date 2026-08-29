"""Validated AI and MCP-facing contracts for FloatChatAI.

These models define the shape of AI intent extraction, query planning, visualization
requests, and response packaging. They intentionally avoid SQL or database
implementation details.
"""

from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StringConstraints, field_validator, model_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
FloatId = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Za-z0-9_-]+$")]

class StrictModel(BaseModel):
    """Base model that rejects undeclared fields."""

    model_config = ConfigDict(extra="forbid")


class IntentType(str, Enum):
    """Supported natural-language query intents."""

    FLOAT_SEARCH = "float_search"
    NEAREST_FLOAT = "nearest_float"
    PROFILE_QUERY = "profile_query"
    TRAJECTORY = "trajectory"
    TIME_SERIES = "time_series"
    COMPARISON = "comparison"
    STATISTICS = "statistics"
    METADATA = "metadata"


class OceanParameter(str, Enum):
    """Supported oceanographic parameters for initial AI planning."""

    TEMPERATURE = "temperature"
    SALINITY = "salinity"
    PRESSURE = "pressure"
    OXYGEN = "oxygen"
    CHLOROPHYLL = "chlorophyll"
    NITRATE = "nitrate"
    PH = "ph"


class MCPToolName(str, Enum):
    """Planned MCP tools exposed through the controlled data interface."""

    SEARCH_FLOATS = "search_floats"
    NEAREST_FLOATS = "nearest_floats"
    GET_PROFILE = "get_profile"
    GET_TRAJECTORY = "get_trajectory"
    QUERY_MEASUREMENTS = "query_measurements"
    GET_STATISTICS = "get_statistics"
    GET_FLOAT_METADATA = "get_float_metadata"


class VisualizationType(str, Enum):
    """Visualization outputs supported by the FloatChatAI contract."""

    MAP = "map"
    PROFILE_CHART = "profile_chart"
    PROFILE = "profile"
    TRAJECTORY_MAP = "trajectory_map"
    TRAJECTORY = "trajectory"
    TIME_SERIES = "time_series"
    DEPTH_TIME = "depth-time"
    COMPARISON_CHART = "comparison_chart"
    COMPARISON = "comparison"
    STATISTICS = "statistics"
    TABLE = "table"


class DateRange(StrictModel):
    """Inclusive date range for a request."""

    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_order(self) -> "DateRange":
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date")
        return self


class DepthRange(StrictModel):
    """Depth interval in meters."""

    min_depth_m: float | None = Field(default=None, ge=0)
    max_depth_m: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> "DepthRange":
        if self.min_depth_m is not None and self.max_depth_m is not None and self.min_depth_m > self.max_depth_m:
            raise ValueError("min_depth_m must be less than or equal to max_depth_m")
        return self


class PressureRange(StrictModel):
    """Pressure interval in decibar."""

    min_pressure_dbar: float | None = Field(default=None, ge=0)
    max_pressure_dbar: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> "PressureRange":
        if (
            self.min_pressure_dbar is not None
            and self.max_pressure_dbar is not None
            and self.min_pressure_dbar > self.max_pressure_dbar
        ):
            raise ValueError("min_pressure_dbar must be less than or equal to max_pressure_dbar")
        return self


class Location(StrictModel):
    """Named or coordinate-based location reference."""

    name: NonEmptyString | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_km: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def require_reference(self) -> "Location":
        if self.name is None and (self.latitude is None or self.longitude is None):
            raise ValueError("location requires a name or both latitude and longitude")
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        return self


class Intent(StrictModel):
    """Structured representation of the user's ARGO question."""

    intent_type: IntentType
    parameters: list[OceanParameter] = Field(default_factory=list)
    region: NonEmptyString | None = None
    location: Location | None = None
    date_range: DateRange | None = None
    depth_range_m: DepthRange | None = None
    pressure_range_dbar: PressureRange | None = None
    float_id: FloatId | None = None
    platform_number: FloatId | None = None
    comparison_targets: list[NonEmptyString] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    original_question: NonEmptyString | None = None

    @field_validator("parameters")
    @classmethod
    def reject_duplicate_parameters(cls, value: list[OceanParameter]) -> list[OceanParameter]:
        if len(value) != len(set(value)):
            raise ValueError("parameters must not contain duplicates")
        return value

    @field_validator("comparison_targets")
    @classmethod
    def reject_duplicate_comparison_targets(cls, value: list[str]) -> list[str]:
        normalized = [item.casefold() for item in value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("comparison_targets must not contain duplicates")
        return value


class VisualizationSpec(StrictModel):
    """Controlled, frontend-independent visualization specification."""

    type: VisualizationType
    title: NonEmptyString | None = None
    variables: list[OceanParameter] = Field(default_factory=list)
    x_axis: NonEmptyString | None = None
    y_axis: NonEmptyString | None = None
    color_field: NonEmptyString | None = None
    latitude_field: NonEmptyString | None = None
    longitude_field: NonEmptyString | None = None
    depth_field: NonEmptyString | None = None
    time_field: NonEmptyString | None = None
    units: dict[str, str] = Field(default_factory=dict)
    data_reference: NonEmptyString | None = None
    options: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("variables")
    @classmethod
    def reject_duplicate_variables(cls, value: list[OceanParameter]) -> list[OceanParameter]:
        if len(value) != len(set(value)):
            raise ValueError("variables must not contain duplicates")
        return value


class QueryMetadata(StrictModel):
    """Trace and provenance metadata for a planned query."""

    request_id: NonEmptyString | None = None
    planner_version: NonEmptyString | None = None
    notes: list[NonEmptyString] = Field(default_factory=list)


SQL_KEY_PATTERN = re.compile(r"(^|_)(raw_)?sql($|_)|sql_query", re.IGNORECASE)
SQL_TEXT_PATTERN = re.compile(r"\b(select|insert|update|delete|drop|alter|create|truncate)\b", re.IGNORECASE)
PARAMETER_ARGUMENT_KEYS = {"parameter", "parameters", "variable", "variables"}


def _reject_sql_like_content(value: Any, path: str = "arguments") -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} keys must be strings")
            if SQL_KEY_PATTERN.search(key):
                raise ValueError("QueryPlan must not contain SQL fields")
            _reject_sql_like_content(nested_value, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            _reject_sql_like_content(nested_value, f"{path}[{index}]")
    elif isinstance(value, str) and SQL_TEXT_PATTERN.search(value):
        raise ValueError("QueryPlan must not contain raw SQL text")


def _validate_parameter_argument(value: Any, path: str) -> None:
    valid_parameters = {parameter.value for parameter in OceanParameter}

    if isinstance(value, str):
        if value not in valid_parameters:
            raise ValueError(f"{path} contains unsupported ocean parameter: {value}")
    elif isinstance(value, list):
        if not value:
            raise ValueError(f"{path} must not be empty")
        for index, item in enumerate(value):
            if not isinstance(item, str) or item not in valid_parameters:
                raise ValueError(f"{path}[{index}] contains unsupported ocean parameter: {item}")
    else:
        raise ValueError(f"{path} must be a supported ocean parameter or list of parameters")


def _validate_known_argument_shapes(arguments: dict[str, JsonValue]) -> None:
    for key, value in arguments.items():
        if key in PARAMETER_ARGUMENT_KEYS:
            _validate_parameter_argument(value, f"arguments.{key}")


class QueryPlan(StrictModel):
    """Structured request from the AI layer to the controlled MCP interface."""

    tool: MCPToolName
    arguments: dict[str, JsonValue]
    visualization: VisualizationSpec | None = None
    metadata: QueryMetadata | None = None

    @model_validator(mode="after")
    def validate_arguments(self) -> "QueryPlan":
        _reject_sql_like_content(self.arguments)
        _validate_known_argument_shapes(self.arguments)
        return self


class ClarificationRequirement(StrictModel):
    """Structured clarification request for underspecified or unsupported queries."""

    reason: NonEmptyString
    missing_fields: list[NonEmptyString] = Field(default_factory=list)
    questions: list[NonEmptyString] = Field(min_length=1)
    original_question: NonEmptyString | None = None


class AIResponseError(StrictModel):
    """Machine-readable error included in an AI response envelope."""

    code: NonEmptyString
    message: NonEmptyString
    details: dict[str, JsonValue] = Field(default_factory=dict)


class AIResponse(StrictModel):
    """Structured response envelope for AI-generated answers and visualizations."""

    answer: NonEmptyString | None = None
    intent: Intent | None = None
    query_plan: QueryPlan | None = None
    clarification: ClarificationRequirement | None = None
    structured_data: JsonValue = None
    visualization: VisualizationSpec | None = None
    metadata: dict[str, JsonValue] = Field(default_factory=dict)
    sources: list[NonEmptyString] = Field(default_factory=list)
    warnings: list[NonEmptyString] = Field(default_factory=list)
    errors: list[AIResponseError] = Field(default_factory=list)
