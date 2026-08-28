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
    """Return a data validation report for an ARGO measurement table."""

    def invalid_count(condition):
        return int(condition.fillna(True).sum())

    problems = {
        "floats": int(df["float_id"].nunique()),
        "profiles": int(df["profile_id"].nunique())
        if "profile_id" in df.columns
        else int(df["float_id"].nunique()),
        "measurements": len(df),
        "invalid_latitude": invalid_count(
            ~df["latitude"].between(-90, 90)
        ),
        "invalid_longitude": invalid_count(
            ~df["longitude"].between(-180, 180)
        ),
        "missing_timestamps": int(
            pd.to_datetime(df["date"], errors="coerce").isna().sum()
        ) if "date" in df.columns else len(df),
        "invalid_pressure": invalid_count(
            (df["pressure_dbar"] < 0)
            | ~df["pressure_dbar"].notna()
        ),
        "invalid_depth": invalid_count(
            (df["depth_m"] < 0)
            | ~df["depth_m"].notna()
        ) if "depth_m" in df.columns else 0,
        "invalid_temperature": invalid_count(
            ~df["temperature_C"].between(-3, 40)
        ),
        "invalid_salinity": invalid_count(
            ~df["salinity"].between(0, 45)
        ),
        "invalid_oxygen": invalid_count(
            df["dissolved_oxygen_umol_kg"] < 0
        ),
        "invalid_chlorophyll": invalid_count(
            df["chlorophyll_mg_m3"] < 0
        ),
    }

    if "profile_id" in df.columns:
        problems["orphan_measurements"] = int(
            df["profile_id"].isna().sum()
        )
    else:
        problems["orphan_measurements"] = 0

    if "float_id" in df.columns and "profile_id" in df.columns:
        profile_floats = df.groupby("profile_id")["float_id"].nunique()
        problems["orphan_profiles"] = int((profile_floats == 0).sum())
    else:
        problems["orphan_profiles"] = 0

    check_keys = [
        "invalid_latitude",
        "invalid_longitude",
        "missing_timestamps",
        "invalid_pressure",
        "invalid_depth",
        "invalid_temperature",
        "invalid_salinity",
        "invalid_oxygen",
        "invalid_chlorophyll",
        "orphan_measurements",
        "orphan_profiles",
    ]
    problems["status"] = (
        "PASS" if all(problems[key] == 0 for key in check_keys)
        else "FAIL"
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