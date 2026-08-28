"""Backend-friendly service functions for the ARGO analytics pipeline.

These functions return plain Python dictionaries and lists so FastAPI, Flask,
or an MCP tool can serialize the results directly as JSON.
"""

from pathlib import Path

from analysis import (
    depth_statistics,
    float_profile,
    overall_statistics,
    parameter_correlation,
    region_statistics,
)
from cleaning import clean_data, load_data, validate_data


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = PROJECT_ROOT / "argo_20_global_demo_extended.xlsx"


def get_dataset(file_path=DEFAULT_DATA_FILE):
    """Load and clean the ARGO dataset for API requests."""
    return clean_data(load_data(file_path))


def get_validation_report(file_path=DEFAULT_DATA_FILE):
    """Return the validation report as JSON-compatible data."""
    return validate_data(get_dataset(file_path), print_report=False)


def _records(frame):
    """Convert a DataFrame to records while replacing missing values."""
    return frame.astype(object).where(frame.notna(), None).to_dict(orient="records")


def get_overall_statistics(file_path=DEFAULT_DATA_FILE):
    """Return descriptive statistics grouped by parameter."""
    statistics = overall_statistics(get_dataset(file_path))
    return {
        parameter: {
            metric: None if value != value else float(value)
            for metric, value in values.items()
        }
        for parameter, values in statistics.to_dict().items()
    }


def get_depth_statistics(file_path=DEFAULT_DATA_FILE):
    """Return measurements aggregated by pressure level."""
    return _records(depth_statistics(get_dataset(file_path)))


def get_region_statistics(file_path=DEFAULT_DATA_FILE):
    """Return measurements aggregated by region."""
    return _records(region_statistics(get_dataset(file_path)))


def get_correlation_matrix(file_path=DEFAULT_DATA_FILE):
    """Return the parameter correlation matrix as JSON-compatible data."""
    return _records(
        parameter_correlation(get_dataset(file_path).reset_index())
    )


def get_float_profile(float_id, file_path=DEFAULT_DATA_FILE):
    """Return one float profile, or an empty list when it does not exist."""
    if not float_id:
        raise ValueError("float_id is required")
    return _records(float_profile(get_dataset(file_path), float_id))


def get_api_catalog():
    """Describe suggested routes for the backend integration."""
    return {
        "GET /api/validation": "get_validation_report()",
        "GET /api/statistics/overall": "get_overall_statistics()",
        "GET /api/statistics/depth": "get_depth_statistics()",
        "GET /api/statistics/region": "get_region_statistics()",
        "GET /api/statistics/correlation": "get_correlation_matrix()",
        "GET /api/floats/{float_id}/profile": "get_float_profile(float_id)",
    }
