# ARGO Scientific Glossary

## Core Terms

| Term | Definition | Database field | Unit | Interpretation |
|---|---|---|---|---|
| ARGO | Global network of autonomous profiling floats. | `float_id` | None | A float collects repeated vertical profiles. |
| Profiling float | Autonomous instrument that descends and ascends while recording ocean observations. | `float_id` | None | One float can produce many profiles. |
| Profile | A vertical set of measurements collected during one float cycle at approximately one location and time. | `profile_id` when available; otherwise `float_id` and `date` | None | Measurements in a profile should be interpreted together by depth or pressure. |
| Trajectory | The sequence of geographic positions of a float across time. | `latitude`, `longitude`, `date` | degrees, timestamp | A trajectory describes movement, not a vertical profile. |
| Pressure | The measured pressure used to represent observation level in the water column. | `pressure_dbar` | dbar | Pressure is related to depth but is not automatically identical to depth. |
| Depth | Vertical distance below the surface. | `depth_m` | m | Do not substitute depth for pressure without an explicit conversion. |
| Temperature | Seawater temperature. | `temperature_C` | deg C | Extreme or physically impossible values should be flagged. |
| Salinity | Practical measure of dissolved salt content. | `salinity` | PSU | Missing salinity is not zero. |
| Oxygen | Dissolved oxygen concentration. | `dissolved_oxygen_umol_kg` | umol/kg | Negative oxygen is invalid. |
| Chlorophyll | A proxy for phytoplankton biomass. | `chlorophyll_mg_m3` | mg/m3 | Negative values are invalid. |
| Nitrate | Dissolved nutrient concentration. | `nitrate_umol_kg` | umol/kg | Interpret with depth, region, and season. |
| QC | Quality control assessment applied to an observation. | `qc` when available | None | QC flags should be considered before scientific interpretation. |
| BGC | Biogeochemical observations, including oxygen, chlorophyll, and nitrate. | Parameter fields | Parameter-specific | BGC variables have different units and valid ranges. |

## Interpretation Rules

- Missing values must not be interpreted as zero.
- Every measurement should belong to a valid profile when `profile_id` is available.
- Every profile should reference a valid float.
- Latitude must be between -90 and 90 degrees; longitude must be between -180 and 180 degrees.
- Pressure and depth cannot be negative.
- Dates must be parsed as valid timestamps before temporal analysis.
- Statistics should report the parameter, unit, count, and filtering conditions.
- Correlation does not prove causation.
