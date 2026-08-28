---
category: parameters
topic: variable_mappings
source: SCIENTIFIC_GLOSSARY.md and prototype analysis scripts
version: 2026-08-foundation
---
# Parameter Meanings And Field Mappings

Temperature means seawater temperature. The prototype field is `temperature_C`, and the glossary unit is deg C.

Salinity is the practical measure of dissolved salt content. The field is `salinity`, and the glossary unit is PSU. Missing salinity is not zero.

Pressure is the measured pressure used to represent observation level in the water column. The field is `pressure_dbar`, and the unit is dbar. Pressure is related to depth but is not automatically identical to depth.

Depth is vertical distance below the surface. The field is `depth_m`, and the unit is m. Do not substitute depth for pressure without an explicit conversion.

Oxygen refers to dissolved oxygen concentration. The prototype field is `dissolved_oxygen_umol_kg`, and the glossary unit is umol/kg. Negative oxygen is invalid.

Chlorophyll is used as a proxy for phytoplankton biomass. The prototype field is `chlorophyll_mg_m3`, and the glossary unit is mg/m3. Negative chlorophyll values are invalid.

Nitrate is dissolved nutrient concentration. The prototype field is `nitrate_umol_kg`, and the glossary unit is umol/kg.

pH is supported by the AI contract as `ph`; the prototype analysis script references `pH`.

Density appears in prototype analysis as `density_kg_m3`, but density is not currently one of the AI query-understanding parameter enum values.
