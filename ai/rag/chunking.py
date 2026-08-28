"""Deterministic chunking for curated RAG knowledge documents."""

from __future__ import annotations

import hashlib
import re

from ai.rag.types import KnowledgeChunk, KnowledgeDocument


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(?P<title>.+)$")


class DocumentChunker:
    """Split Markdown documents while preserving headings and metadata."""

    def __init__(self, *, max_chars: int = 900) -> None:
        if max_chars < 200:
            raise ValueError("max_chars must be at least 200")
        self.max_chars = max_chars

    def chunk_documents(self, documents: list[KnowledgeDocument]) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for document in documents:
            chunks.extend(self.chunk_document(document))
        return chunks

    def chunk_document(self, document: KnowledgeDocument) -> list[KnowledgeChunk]:
        sections = _split_markdown_sections(document.text)
        chunks: list[KnowledgeChunk] = []
        chunk_index = 0
        for heading, section_text in sections:
            for part in _split_section(section_text, self.max_chars):
                chunk_id = _chunk_id(document.id, chunk_index, part)
                metadata = document.metadata | {"document_id": document.id}
                if heading:
                    metadata["heading"] = heading
                chunks.append(KnowledgeChunk(id=chunk_id, text=part, metadata=metadata))
                chunk_index += 1
        return chunks


def _split_markdown_sections(text: str) -> list[tuple[str | None, str]]:
    sections: list[tuple[str | None, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        heading_match = HEADING_PATTERN.match(line)
        if heading_match and current_lines:
            sections.append((current_heading, current_lines))
            current_heading = heading_match.group("title").strip()
            current_lines = [line]
        else:
            if heading_match:
                current_heading = heading_match.group("title").strip()
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    return [(heading, "\n".join(lines).strip()) for heading, lines in sections if "\n".join(lines).strip()]


def _split_section(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = paragraph

    if current:
        chunks.append(current)
    return chunks


def _chunk_id(document_id: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{document_id}:{chunk_index:03d}:{digest}"
