import pandas as pd


def overall_statistics(df):

    parameters = [
        "temperature_C",
        "salinity",
        "dissolved_oxygen_umol_kg",
        "chlorophyll_mg_m3",
        "nitrate_umol_kg",
        "pH",
        "density_kg_m3"
    ]

    return df[parameters].describe()


def depth_statistics(df):

    result = (
        df.groupby("pressure_dbar")
        .agg(
            mean_temperature=(
                "temperature_C",
                "mean"
            ),

            min_temperature=(
                "temperature_C",
                "min"
            ),

            max_temperature=(
                "temperature_C",
                "max"
            ),

            mean_salinity=(
                "salinity",
                "mean"
            ),

            mean_oxygen=(
                "dissolved_oxygen_umol_kg",
                "mean"
            ),

            mean_chlorophyll=(
                "chlorophyll_mg_m3",
                "mean"
            )
        )
        .reset_index()
    )

    return result


def region_statistics(df):

    return (
        df.groupby("region")
        .agg(
            mean_temperature=(
                "temperature_C",
                "mean"
            ),

            mean_salinity=(
                "salinity",
                "mean"
            ),

            mean_oxygen=(
                "dissolved_oxygen_umol_kg",
                "mean"
            ),

            mean_chlorophyll=(
                "chlorophyll_mg_m3",
                "mean"
            )
        )
        .reset_index()
    )


def parameter_correlation(df):

    parameters = [
        "temperature_C",
        "salinity",
        "dissolved_oxygen_umol_kg",
        "chlorophyll_mg_m3",
        "nitrate_umol_kg",
        "pH",
        "density_kg_m3"
    ]

    return df[parameters].corr()


def float_profile(df, float_id):

    return (
        df[df["float_id"] == float_id]
        .sort_values("pressure_dbar")
    )