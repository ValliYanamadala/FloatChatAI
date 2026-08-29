"""End-to-end FloatChatAI agent orchestrator connecting all architectural layers."""

from __future__ import annotations

import logging
from typing import Any

from ai.agent.query_understanding import QueryUnderstandingService
from ai.agent.response_generator import ResponseGenerator
from ai.rag.context import ContextBuilder
from ai.rag.retrieval import RAGRetriever
from ai.schemas.contracts import AIResponse, AIResponseError
from app.adapters.query_plan_adapter import QueryPlanAdapter

LOGGER = logging.getLogger(__name__)


class FloatChatAgent:
    """
    Unified FloatChatAI orchestrator:
    User Question -> QueryUnderstanding -> QueryPlan -> MCP / Backend -> ResponseGenerator -> Final AIResponse
    """

    def __init__(
        self,
        query_understanding: QueryUnderstandingService,
        response_generator: ResponseGenerator,
        *,
        retriever: RAGRetriever | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self._query_understanding = query_understanding
        self._response_generator = response_generator
        self._retriever = retriever
        self._context_builder = context_builder or ContextBuilder()

    async def answer(self, question: str) -> AIResponse:
        """
        Execute the full FloatChatAI natural-language query and response pipeline.
        """
        normalized = question.strip()
        LOGGER.info("floatchat_agent.question_received", extra={"question": normalized})

        # 1. Domain Knowledge Retrieval (RAG)
        rag_context: str | None = None
        sources: list[str] = []
        if self._retriever is not None:
            try:
                retrieved_chunks = self._retriever.retrieve(normalized)
                if retrieved_chunks:
                    rag_context = self._context_builder.build(retrieved_chunks)
                    sources = [
                        f"{c.metadata.get('topic', 'ARGO')}: {c.metadata.get('source', 'knowledge_base')}"
                        for c in retrieved_chunks
                        if c.metadata
                    ]
            except Exception as exc:
                LOGGER.info("floatchat_agent.rag_retrieval_failed", extra={"reason": str(exc)})

        # 2. Query Understanding (Intent & QueryPlan Extraction)
        understanding = await self._query_understanding.understand(
            normalized,
            context={"rag_context": rag_context} if rag_context else None,
        )

        # If underspecified or requires clarification, return immediately
        if understanding.clarification:
            return understanding

        query_plan = understanding.query_plan
        intent = understanding.intent

        # 3. Controlled MCP Tool Dispatch & Backend Execution
        structured_data: Any = None
        errors: list[AIResponseError] = []
        if query_plan:
            try:
                structured_data = QueryPlanAdapter.execute_via_mcp(query_plan)
            except Exception as exc:
                LOGGER.error("floatchat_agent.mcp_execution_error", extra={"error": str(exc)})
                errors.append(AIResponseError(code="MCP_EXECUTION_ERROR", message=str(exc)))
                structured_data = {"error": str(exc)}

        # 4. Response Generation & Visualization Specification
        final_response = await self._response_generator.generate(
            question=normalized,
            query_plan=query_plan,
            structured_data=structured_data,
            rag_context=rag_context,
            intent=intent,
            sources=sources,
            errors=errors,
        )

        return final_response
