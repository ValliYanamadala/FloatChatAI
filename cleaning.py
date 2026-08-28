import pandas as pd
import numpy as np


def load_data(file_path):
    """Load ARGO data from Excel."""

    df = pd.read_excel(
        file_path,
        sheet_name="ARGO_Data"
    )

    return df


def check_data(df):
    """Display basic information about the dataset."""

    print("\n========== DATA INFORMATION ==========")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nUnique floats:")
    print(df["float_id"].nunique())

    print("\nPressure levels:")
    print(sorted(df["pressure_dbar"].unique()))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())


def validate_data(df):
    """Check whether values fall within reasonable ranges."""

    problems = {}

    # Latitude
    problems["invalid_latitude"] = (
        (~df["latitude"].between(-90, 90)).sum()
    )

    # Longitude
    problems["invalid_longitude"] = (
        (~df["longitude"].between(-180, 180)).sum()
    )

    # Pressure
    problems["invalid_pressure"] = (
        (~df["pressure_dbar"].isin(
            [10, 50, 100, 200, 500, 1000]
        )).sum()
    )

    # Temperature
    problems["invalid_temperature"] = (
        (~df["temperature_C"].between(-3, 40)).sum()
    )

    # Salinity
    problems["invalid_salinity"] = (
        (~df["salinity"].between(0, 45)).sum()
    )

    # Oxygen
    problems["invalid_oxygen"] = (
        (df["dissolved_oxygen_umol_kg"] < 0).sum()
    )

    # Chlorophyll
    problems["invalid_chlorophyll"] = (
        (df["chlorophyll_mg_m3"] < 0).sum()
    )

    print("\n========== VALIDATION ==========")

    for name, count in problems.items():
        print(name, ":", count)

    return problems


def clean_data(df):
    """Clean the ARGO dataset."""

    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows missing essential information
    df = df.dropna(
        subset=[
            "float_id",
            "latitude",
            "longitude",
            "pressure_dbar"
        ]
    )

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Remove impossible values

    df.loc[
        ~df["latitude"].between(-90, 90),
        "latitude"
    ] = np.nan

    df.loc[
        ~df["longitude"].between(-180, 180),
        "longitude"
    ] = np.nan

    df.loc[
        ~df["pressure_dbar"].isin(
            [10, 50, 100, 200, 500, 1000]
        ),
        "pressure_dbar"
    ] = np.nan

    df.loc[
        ~df["temperature_C"].between(-3, 40),
        "temperature_C"
    ] = np.nan

    df.loc[
        ~df["salinity"].between(0, 45),
        "salinity"
    ] = np.nan

    df.loc[
        df["dissolved_oxygen_umol_kg"] < 0,
        "dissolved_oxygen_umol_kg"
    ] = np.nan

    df.loc[
        df["chlorophyll_mg_m3"] < 0,
        "chlorophyll_mg_m3"
    ] = np.nan

    # Sort data
    df = df.sort_values(
        ["float_id", "pressure_dbar"]
    )

    return df