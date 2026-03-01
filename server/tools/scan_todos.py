"""MCP tool: scan a directory for TODO/FIXME and similar markers."""

import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.config import (
    DEFAULT_TAGS,
    IGNORED_DIRS,
    BINARY_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    IGNORED_EXTENSIONS,
)

from server.models import TodoItem


def _collect_todos(root: Path) -> list[TodoItem]:
    """
    Recursively scans a directory for TODO/FIXME markers and similar markers.

    Args:
        root: Path to the directory root.

    Returns:
        list of TodoItem objects found in the directory.

    Raises:
        ValueError: if the path does not exist or is not a directory.
    """
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")
    items: list[TodoItem] = []
    # Паттерн: один из тегов, затем опционально ':', '-', скобки, пробелы и текст
    tags_re = "|".join(re.escape(t) for t in DEFAULT_TAGS)
    tag_pattern = re.compile(
        rf"(?:#|//|/\*|<!--)\s*\b({tags_re})\b\s*[:\-(\[]?\s*(.*)",
        re.IGNORECASE,
    )

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in BINARY_EXTENSIONS:
            continue
        if path.suffix.lower() in IGNORED_EXTENSIONS:
            continue
        if path.name in {
            "poetry.lock",
            "package-lock.json",
            "yarn.lock",
            "Pipfile.lock",
        }:
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
        except OSError:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        rel_path = str(path.relative_to(root)) if path != root else path.name
        for line_no, line in enumerate(text.splitlines(), start=1):
            m = tag_pattern.search(line)
            if not m:
                continue
            tag, rest = m.group(1), (m.group(2) or "").strip()
            items.append(
                TodoItem(
                    tag=tag.upper(),
                    file=rel_path,
                    line=line_no,
                    text=rest or line.strip(),
                    context=line.strip(),
                )
            )

    return items


def register_scan_todos(mcp: FastMCP) -> None:
    """Регистрирует инструмент scan_todos в FastMCP."""

    @mcp.tool()
    def scan_todos(path: str) -> list[dict[str, Any]]:
        """
        Сканирует директорию на маркеры TODO, FIXME, HACK, XXX, NOTE,
        DEPRECATED.

        Обходит текстовые файлы (лимит 1 MB), пропускает __pycache__, .git,
        node_modules, venv и бинарные расширения.

        Args:
            path: Путь к корню директории для сканирования.

        Returns:
            Список словарей: tag, file, line, text, context для каждого
            маркера.
        """
        p = Path(path).resolve()
        if not p.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not p.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        todos = _collect_todos(p)
        return [t.model_dump() for t in todos]
