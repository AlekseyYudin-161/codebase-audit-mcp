"""MCP resource: static view of current audit rules and thresholds."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from server.config import (
    BINARY_EXTENSIONS,
    COMMENTED_BLOCK_THRESHOLD,
    DEFAULT_TAGS,
    HIGH_COMPLEXITY_THRESHOLD,
    IGNORED_DIRS,
    LONG_FUNCTION_THRESHOLD,
    MAX_FILE_SIZE_BYTES,
    SECRET_PATTERNS,
)


def register_audit_rules(mcp: FastMCP) -> None:
    """Register config://audit-rules resource."""

    @mcp.resource(
        "config://audit-rules",
        name="Audit rules configuration",
        mime_type="application/json",
        description=("Current static analysis rules used by codebase-audit-mcp."),
    )
    def audit_rules() -> dict[str, Any]:
        """
        Возвращает актуальную конфигурацию правил аудита:
        TODO‑теги, игнорируемые директории, бинарные расширения,
        лимит размера файла и пороги для code smells.
        """

        secrets = [
            {"pattern": pattern, "description": description}
            for pattern, description in SECRET_PATTERNS
        ]

        return {
            "default_tags": list(DEFAULT_TAGS),
            "ignored_dirs": sorted(IGNORED_DIRS),
            "binary_extensions": sorted(BINARY_EXTENSIONS),
            "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
            "secret_patterns": secrets,
            "long_function_threshold": LONG_FUNCTION_THRESHOLD,
            "high_complexity_threshold": HIGH_COMPLEXITY_THRESHOLD,
            "commented_block_threshold": COMMENTED_BLOCK_THRESHOLD,
        }
