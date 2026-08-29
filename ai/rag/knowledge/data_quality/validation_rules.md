---
category: data_quality
topic: validation_rules
source: SCIENTIFIC_GLOSSARY.md and cleaning.py
version: 2026-08-foundation
---
# Data Quality And Interpretation Rules

Missing values must not be interpreted as zero.

Every measurement should belong to a valid profile when `profile_id` is available.

Every profile should reference a valid float.

Latitude must be between -90 and 90 degrees. Longitude must be between -180 and 180 degrees.

Pressure and depth cannot be negative.

Dates must be parsed as valid timestamps before temporal analysis.

The prototype cleaning script checks temperature with a documented valid range of -3 to 40 deg C and salinity from 0 to 45 PSU.

The prototype cleaning script treats negative dissolved oxygen and negative chlorophyll as invalid.

Statistics should report the parameter, unit, count, and filtering conditions.

Correlation does not prove causation.
