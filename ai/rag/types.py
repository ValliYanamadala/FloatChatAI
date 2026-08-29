"""Typed records used by the FloatChatAI RAG layer."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RAGModel(BaseModel):
    """Base model for RAG data records."""

    model_config = ConfigDict(extra="forbid")


class KnowledgeDocument(RAGModel):
    id: NonEmptyString
    text: NonEmptyString
    metadata: dict[str, str]


class KnowledgeChunk(RAGModel):
    id: NonEmptyString
    text: NonEmptyString
    metadata: dict[str, str]


class RetrievalResult(RAGModel):
    chunk_id: NonEmptyString
    text: NonEmptyString
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, str]


class RAGUsefulness(str, Enum):
    USEFUL = "useful"
    OPTIONAL = "optional"
    NOT_PRIMARY = "not_primary"


class QueryRoute(RAGModel):
    rag_usefulness: RAGUsefulness
    database_required: bool
    reason: NonEmptyString
    suggested_categories: list[str] = Field(default_factory=list)
