---
category: schema
topic: database_semantics
source: AGENTS.md and project foundation requirements
version: 2026-08-foundation
---
# Database Schema Semantics

PostgreSQL with PostGIS is the planned source of truth for structured float, profile, trajectory, and measurement data.

The normalized target data model is organized around regions, floats, profiles, measurements, and trajectories.

Regions organize named ocean or geographic areas used for filtering and comparison.

Floats represent ARGO platforms. One float can produce many profiles and can have a trajectory across time.

Profiles represent vertical observations for a float cycle at approximately one location and time.

Measurements represent observed parameter values at pressure or depth levels within a profile.

Trajectories represent geographic positions of a float across time and describe movement rather than vertical structure.

The LLM must not depend on database implementation details. It should produce validated QueryPlan objects that later flow through MCP/backend tools.
