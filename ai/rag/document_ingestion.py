"""Load curated FloatChatAI RAG knowledge documents."""

from __future__ import annotations

import re
from pathlib import Path

from ai.rag.types import KnowledgeDocument


KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
FRONT_MATTER_PATTERN = re.compile(r"\A---\n(?P<metadata>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)
SQL_STATEMENT_PATTERN = re.compile(r"\b(select|insert|update|delete|drop|alter|create|truncate)\b\s+.+\b(from|into|table|database|measurements)\b", re.IGNORECASE)


class KnowledgeDocumentError(ValueError):
    """Raised when a knowledge document violates RAG corpus rules."""


def load_knowledge_documents(root: Path | None = None) -> list[KnowledgeDocument]:
    """Load all curated Markdown knowledge documents in deterministic order."""

    knowledge_root = root or KNOWLEDGE_DIR
    if not knowledge_root.exists():
        raise KnowledgeDocumentError(f"Knowledge directory does not exist: {knowledge_root}")

    documents: list[KnowledgeDocument] = []
    for path in sorted(knowledge_root.rglob("*.md")):
        documents.append(load_knowledge_document(path, knowledge_root))
    return documents


def load_knowledge_document(path: Path, root: Path | None = None) -> KnowledgeDocument:
    """Load one Markdown knowledge document with simple front-matter metadata."""

    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        raise KnowledgeDocumentError(f"Knowledge document is missing front matter: {path}")

    metadata = _parse_front_matter(match.group("metadata"), path)
    body = match.group("body").strip()
    _validate_knowledge_body(body, path)

    relative_path = path.relative_to(root) if root else path.name
    return KnowledgeDocument(
        id=str(relative_path.with_suffix("")).replace("/", ":"),
        text=body,
        metadata=metadata | {"path": str(relative_path)},
    )


def _parse_front_matter(raw_metadata: str, path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in raw_metadata.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise KnowledgeDocumentError(f"Invalid metadata line in {path}: {line}")
        key, value = stripped.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')

    required = {"category", "topic", "source", "version"}
    missing = sorted(required - set(metadata))
    if missing:
        raise KnowledgeDocumentError(f"Missing metadata keys in {path}: {', '.join(missing)}")
    return metadata


def _validate_knowledge_body(text: str, path: Path) -> None:
    if SQL_STATEMENT_PATTERN.search(text):
        raise KnowledgeDocumentError(f"Knowledge document contains SQL-like executable text: {path}")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if _looks_like_raw_measurement_row(line):
            raise KnowledgeDocumentError(f"Knowledge document may contain raw measurement rows at {path}:{line_number}")


def _looks_like_raw_measurement_row(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("|---"):
        return False
    delimiter = "," if "," in stripped else "\t" if "\t" in stripped else None
    if delimiter is None:
        return False

    cells = [cell.strip() for cell in stripped.split(delimiter)]
    if len(cells) < 5:
        return False

    numeric_cells = 0
    for cell in cells:
        try:
            float(cell)
        except ValueError:
            continue
        numeric_cells += 1
    return numeric_cells >= 4
