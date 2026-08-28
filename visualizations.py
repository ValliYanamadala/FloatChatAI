from cleaning import (
    load_data,
    check_data,
    validate_data,
    clean_data
)

from analysis import (
    overall_statistics,
    depth_statistics,
    region_statistics,
    parameter_correlation,
    float_profile
)

FILE = "argo_20_global_demo_extended.xlsx"


# =========================
# 1. LOAD
# =========================

df = load_data(FILE)

print("Original dataset:")
print(df.head())


# =========================
# 2. CHECK
# =========================

check_data(df)


# =========================
# 3. VALIDATE
# =========================

validate_data(df)


# =========================
# 4. CLEAN
# =========================

df = clean_data(df)

print("\nCleaned dataset:")
print(df.head())


# =========================
# 5. STATISTICS
# =========================

print("\n========== OVERALL STATISTICS ==========")
print(overall_statistics(df))


print("\n========== DEPTH STATISTICS ==========")
print(depth_statistics(df))


print("\n========== REGION STATISTICS ==========")
print(region_statistics(df))


print("\n========== CORRELATION ==========")
print(parameter_correlation(df))


# =========================
# 6. FLOAT PROFILE
# =========================

selected_float = float_profile(
    df,
    "ARGO_001"
)

print("\n========== ARGO_001 PROFILE ==========")
print(selected_float)


