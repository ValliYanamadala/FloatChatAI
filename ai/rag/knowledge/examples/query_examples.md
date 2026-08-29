---
category: examples
topic: representative_queries
source: tests/fixtures/natural_language_questions.json and ground_truth_questions.json
version: 2026-08-foundation
---
# Representative Query Examples

"Show me ARGO floats in the Arabian Sea." maps to float search and the future `search_floats` MCP tool.

"Which ARGO floats are closest to Chennai?" maps to nearest-float search and the future `nearest_floats` MCP tool.

"Show salinity profiles near the equator." maps to a profile-style measurement query using salinity and a regional location.

"Show the trajectory of float 2901234." maps to trajectory lookup for a float identifier.

"Show temperature changes over the last six months." asks for a time series, but may need clarification if no region, float, or other scope is supplied.

"Compare salinity in the Arabian Sea and Bay of Bengal." maps to comparison over two region targets.

"What is the average temperature?" asks for statistics, but may need clarification if no scope is supplied.

"What parameters does float 2901234 measure?" maps to float metadata lookup.

"Show salinity measurements between 100 and 500 dbar." uses a pressure range, not a depth range.
