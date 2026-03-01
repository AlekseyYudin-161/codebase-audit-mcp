"""MCP tool: generate aggregated health report for a codebase."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.models import HealthReport, SmellItem, TodoItem
from server.state import set_last_report
from server.tools.find_code_smells import _collect_smells, _iter_text_files
from server.tools.scan_todos import _collect_todos


def _build_summary(smells: list[SmellItem], todos: list[TodoItem]) -> dict[str, int]:
    """Aggregate counts by severity and TODO markers."""
    high = sum(1 for s in smells if s.severity == "high")
    medium = sum(1 for s in smells if s.severity == "medium")
    low = sum(1 for s in smells if s.severity == "low")
    return {
        "high": high,
        "medium": medium,
        "low": low,
        "todos": len(todos),
    }


def _count_scanned_files(root: Path) -> int:
    """Count number of text files scanned using shared iterator."""
    return sum(1 for _path, _text in _iter_text_files(root))


def register_generate_report(mcp: FastMCP) -> None:
    """Register generate_report tool in FastMCP."""

    @mcp.tool()
    def generate_report(path: str) -> dict[str, Any]:
        """
        Генерирует сводный HealthReport по директории.

        Использует scan_todos и find_code_smells для поиска TODO и code smells,
        собирает агрегированный отчёт и сохраняет его в in-memory state.

        Args:
            path: Путь к корню проекта для анализа.

        Returns:
            HealthReport как словарь (path, timestamp, files_scanned,
            todos, smells, summary).
        """
        root = Path(path).resolve()
        if not root.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not root.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        todos = _collect_todos(root)
        smells = _collect_smells(root)
        files_scanned = _count_scanned_files(root)

        report = HealthReport(
            path=str(root),
            timestamp=datetime.now(timezone.utc).isoformat(),
            files_scanned=files_scanned,
            todos=todos,
            smells=smells,
            summary=_build_summary(smells, todos),
        )

        set_last_report(report)
        return report.model_dump()
