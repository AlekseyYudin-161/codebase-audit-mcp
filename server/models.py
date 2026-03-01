"""Pydantic models for responses"""

from typing import Optional
from pydantic import BaseModel


class TodoItem(BaseModel):
    """TODO marker in a file"""
    tag: str
    file: str
    line: int
    text: str
    context: str


class SmellItem(BaseModel):
    """Smell in a file"""
    category: str
    severity: str  # "high" | "medium" | "low"
    file: str
    line: int
    line_end: Optional[int]
    description: str
    snippet: str


class HealthReport(BaseModel):
    """Health report"""
    path: str
    timestamp: str
    files_scanned: int
    todos: list[TodoItem]
    smells: list[SmellItem]
    summary: dict[str, int]  # {"high": 3, "medium": 7, "low": 12, "todos": 5}
