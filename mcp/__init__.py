"""Model Context Protocol (MCP) server package for FloatChatAI."""

import os
import sys

# Extend local 'mcp' package search path to include installed site-packages 'mcp' SDK
for _p in sys.path:
    if "site-packages" in _p:
        _sp_mcp = os.path.join(_p, "mcp")
        if os.path.isdir(_sp_mcp) and _sp_mcp not in __path__:
            __path__.append(_sp_mcp)

from mcp.server import (
    mcp,
    get_backend_url,
    api_get,
    api_post,
    search_floats,
    nearest_floats,
    get_profile,
    get_trajectory,
    query_measurements,
    get_statistics,
    get_float_metadata,
)

__all__ = [
    "mcp",
    "get_backend_url",
    "api_get",
    "api_post",
    "search_floats",
    "nearest_floats",
    "get_profile",
    "get_trajectory",
    "query_measurements",
    "get_statistics",
    "get_float_metadata",
]
