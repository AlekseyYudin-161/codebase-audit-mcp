"""MCP tool: find code smells (secrets, eval/exec, long functions, complexity)."""

import ast
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.config import (
    IGNORED_DIRS,
    BINARY_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    SECRET_PATTERNS,
    LONG_FUNCTION_THRESHOLD,
    HIGH_COMPLEXITY_THRESHOLD,
    COMMENTED_BLOCK_THRESHOLD,
)
from server.models import SmellItem


def _iter_text_files(root: Path):
    """Обходит текстовые файлы в root (те же правила, что в scan_todos)."""
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in BINARY_EXTENSIONS:
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
        yield path, text


def _smells_secrets(path: Path, text: str, rel_path: str) -> list[SmellItem]:
    items: list[SmellItem] = []
    lines = text.splitlines()
    for pattern, description in SECRET_PATTERNS:
        for i, line in enumerate(lines, start=1):
            if re.search(pattern, line):
                items.append(
                    SmellItem(
                        category="secret",
                        severity="high",
                        file=rel_path,
                        line=i,
                        line_end=None,
                        description=description,
                        snippet=line.strip()[:200],
                    )
                )
    # Multiline: private key
    for pattern, description in SECRET_PATTERNS:
        if "PRIVATE KEY" in description.upper():
            m = re.search(pattern, text, re.DOTALL)
            if m:
                start = text[: m.start()].count("\n") + 1
                items.append(
                    SmellItem(
                        category="secret",
                        severity="high",
                        file=rel_path,
                        line=start,
                        line_end=None,
                        description=description,
                        snippet=m.group(0)[:200],
                    )
                )
    return items


def _smells_eval_exec(path: Path, text: str, rel_path: str) -> list[SmellItem]:
    items: list[SmellItem] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("#"):
            continue
        if "Use of eval()" in line or "Use of exec()" in line:
            continue
        if re.search(r"\beval\s*\(", line):
            items.append(
                SmellItem(
                    category="dangerous_call",
                    severity="high",
                    file=rel_path,
                    line=i,
                    line_end=None,
                    description="Use of eval()",
                    snippet=line.strip()[:200],
                )
            )
        if re.search(r"\bexec\s*\(", line):
            items.append(
                SmellItem(
                    category="dangerous_call",
                    severity="high",
                    file=rel_path,
                    line=i,
                    line_end=None,
                    description="Use of exec()",
                    snippet=line.strip()[:200],
                )
            )
    return items


def _complexity(node: ast.AST) -> int:
    """Подсчёт ветвлений (упрощённая цикломатическая сложность)."""
    n = 0
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.ExceptHandler,
                ast.With,
                ast.Assert,
                ast.comprehension,
            ),
        ):
            n += 1
        if isinstance(child, ast.BoolOp):
            n += len(child.values) - 1
    return n


def _smells_python_ast(path: Path, text: str, rel_path: str) -> list[SmellItem]:
    items: list[SmellItem] = []
    if path.suffix.lower() != ".py":
        return items
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return items

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end_line = node.end_lineno or node.lineno
            length = end_line - node.lineno + 1
            if length >= LONG_FUNCTION_THRESHOLD:
                items.append(
                    SmellItem(
                        category="long_function",
                        severity="medium",
                        file=rel_path,
                        line=node.lineno,
                        line_end=end_line,
                        description=f"Function has {length} lines (>= {LONG_FUNCTION_THRESHOLD})",
                        snippet=node.name,
                    )
                )
            comp = _complexity(node)
            if comp >= HIGH_COMPLEXITY_THRESHOLD:
                items.append(
                    SmellItem(
                        category="high_complexity",
                        severity="high",
                        file=rel_path,
                        line=node.lineno,
                        line_end=end_line,
                        description=f"High complexity: {comp} branches (>= {HIGH_COMPLEXITY_THRESHOLD})",
                        snippet=node.name,
                    )
                )

    # Commented block: последовательные строки комментариев
    line_list = text.splitlines()
    i = 0
    while i < len(line_list):
        line = line_list[i]
        if not line.strip().startswith("#"):
            i += 1
            continue
        start_line_no = i + 1
        count = 0
        while i < len(line_list) and line_list[i].strip().startswith("#"):
            count += 1
            i += 1
        if count >= COMMENTED_BLOCK_THRESHOLD:
            items.append(
                SmellItem(
                    category="commented_block",
                    severity="low",
                    file=rel_path,
                    line=start_line_no,
                    line_end=start_line_no + count - 1,
                    description=(
                        f"{count} consecutive comment lines "
                        f"(>= {COMMENTED_BLOCK_THRESHOLD})"
                    ),
                    snippet="",
                )
            )

    return items


def _collect_smells(root: Path) -> list[SmellItem]:
    """
    Recursively scans a directory for code smells.

    Args:
        root: Path to the directory root.

    Returns:
        list of SmellItem objects found in the directory.

    Raises:
        ValueError: if the path does not exist or is not a directory.
    """
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")
    items: list[SmellItem] = []
    for path, text in _iter_text_files(root):
        rel_path = str(path.relative_to(root)) if path != root else path.name
        items.extend(_smells_secrets(path, text, rel_path))
        items.extend(_smells_eval_exec(path, text, rel_path))
        items.extend(_smells_python_ast(path, text, rel_path))
    return items


def register_find_code_smells(mcp: FastMCP) -> None:
    """Регистрирует инструмент find_code_smells в FastMCP."""

    @mcp.tool()
    def find_code_smells(path: str) -> list[dict[str, Any]]:
        """
        Ищет code smells в директории: секреты, eval/exec, длинные функции,
        высокая сложность, большие блоки комментариев.

        Использует config: SECRET_PATTERNS, LONG_FUNCTION_THRESHOLD,
        HIGH_COMPLEXITY_THRESHOLD, COMMENTED_BLOCK_THRESHOLD.

        Args:
            path: Путь к корню директории для сканирования.

        Returns:
            Список словарей SmellItem: category, severity, file, line,
            line_end, description, snippet.
        """
        p = Path(path).resolve()
        if not p.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not p.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        smells = _collect_smells(p)
        return [s.model_dump() for s in smells]
