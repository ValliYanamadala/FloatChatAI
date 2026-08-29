"""Lightweight routing support for deciding when RAG is useful."""

from __future__ import annotations

import re

from ai.rag.types import QueryRoute, RAGUsefulness


KNOWLEDGE_KEYWORDS = {
    "meaning",
    "mean",
    "definition",
    "define",
    "what does",
    "what is",
    "unit",
    "units",
    "psal",
    "pres",
    "temp",
    "doxy",
    "chla",
    "nitrate",
    "bgc",
    "qc",
    "quality control",
    "data mode",
    "schema",
    "profile",
    "trajectory",
}

MEASUREMENT_ACTIONS = {
    "show",
    "plot",
    "map",
    "average",
    "mean",
    "highest",
    "lowest",
    "nearest",
    "closest",
    "compare",
    "measurements",
    "observations",
    "profiles",
    "trajectory",
    "changes",
    "trend",
    "trends",
}

STATISTIC_TERMS = {
    "average",
    "mean temperature",
    "mean salinity",
    "highest",
    "lowest",
    "maximum",
    "minimum",
    "statistics",
}


def classify_rag_usefulness(query: str) -> QueryRoute:
    """Classify whether RAG should support a query without calling an LLM."""

    normalized = query.casefold().strip()
    has_knowledge_signal = any(keyword in normalized for keyword in KNOWLEDGE_KEYWORDS)
    has_measurement_signal = any(re.search(rf"\b{re.escape(keyword)}\b", normalized) for keyword in MEASUREMENT_ACTIONS)

    if has_measurement_signal and not _is_definition_question(normalized):
        categories = ["parameters"] if has_knowledge_signal else []
        return QueryRoute(
            rag_usefulness=RAGUsefulness.NOT_PRIMARY,
            database_required=True,
            reason="The query asks for observations, statistics, locations, or plotted data that must come from MCP/database results.",
            suggested_categories=categories,
        )

    if has_knowledge_signal:
        return QueryRoute(
            rag_usefulness=RAGUsefulness.USEFUL,
            database_required=False,
            reason="The query asks for definitions, terminology, units, schema, QC, or interpretation guidance.",
            suggested_categories=_suggest_categories(normalized),
        )

    return QueryRoute(
        rag_usefulness=RAGUsefulness.OPTIONAL,
        database_required=False,
        reason="No strong RAG or database signal was detected.",
        suggested_categories=[],
    )


def _is_definition_question(normalized: str) -> bool:
    if any(term in normalized for term in STATISTIC_TERMS):
        return False
    return normalized.startswith(("what is ", "what does ", "define ", "meaning of "))


def _suggest_categories(normalized: str) -> list[str]:
    categories: list[str] = []
    if any(
        term in normalized
        for term in (
            "psal",
            "pres",
            "temp",
            "doxy",
            "chla",
            "temperature",
            "salinity",
            "pressure",
            "depth",
            "oxygen",
            "chlorophyll",
            "nitrate",
            "ph",
            "unit",
            "parameter",
        )
    ):
        categories.append("parameters")
    if any(term in normalized for term in ("qc", "quality", "valid", "validation")):
        categories.append("data_quality")
    if any(term in normalized for term in ("schema", "table", "database", "profile", "trajectory")):
        categories.append("schema")
    if any(term in normalized for term in ("argo", "float", "bgc")):
        categories.append("argo")
    return categories
