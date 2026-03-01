"""Tests for generate_report tool."""

from pathlib import Path

import pytest

from server.tools.generate_report import _build_summary, _count_scanned_files
from server.tools.find_code_smells import _collect_smells
from server.tools.scan_todos import _collect_todos
from server.models import HealthReport, SmellItem, TodoItem
from server.state import get_last_report, set_last_report

FIXTURES = Path(__file__).parent / "fixtures"


class TestBuildSummary:
    """Unit tests for _build_summary helper."""

    def _make_smell(self, severity: str) -> SmellItem:
        return SmellItem(
            category="secret",
            severity=severity,
            file="test.py",
            line=1,
            line_end=None,
            description="test",
            snippet="test",
        )

    def _make_todo(self) -> TodoItem:
        return TodoItem(
            tag="TODO",
            file="test.py",
            line=1,
            text="something",
            context="# TODO: something",
        )

    def test_summary_counts_high(self):
        smells = [self._make_smell("high"), self._make_smell("high")]
        summary = _build_summary(smells, [])
        assert summary["high"] == 2

    def test_summary_counts_medium(self):
        smells = [self._make_smell("medium")]
        summary = _build_summary(smells, [])
        assert summary["medium"] == 1

    def test_summary_counts_low(self):
        smells = [self._make_smell("low"), self._make_smell("low")]
        summary = _build_summary(smells, [])
        assert summary["low"] == 2

    def test_summary_counts_todos(self):
        todos = [self._make_todo(), self._make_todo(), self._make_todo()]
        summary = _build_summary([], todos)
        assert summary["todos"] == 3

    def test_summary_has_all_keys(self):
        summary = _build_summary([], [])
        assert set(summary.keys()) == {"high", "medium", "low", "todos"}

    def test_summary_zeros_on_empty_input(self):
        summary = _build_summary([], [])
        assert summary == {"high": 0, "medium": 0, "low": 0, "todos": 0}


class TestCountScannedFiles:
    """Tests for _count_scanned_files helper."""

    def test_returns_positive_int_for_fixtures(self):
        count = _count_scanned_files(FIXTURES)
        assert isinstance(count, int)
        assert count > 0

    def test_counts_at_least_three_fixture_files(self):
        # we have: sample_with_todos, sample_with_smells, sample_clean
        count = _count_scanned_files(FIXTURES)
        assert count >= 3


class TestGenerateReportIntegration:
    """Integration tests: run full report over fixtures directory."""

    def setup_method(self):
        todos = _collect_todos(FIXTURES)
        smells = _collect_smells(FIXTURES)
        files_scanned = _count_scanned_files(FIXTURES)

        from datetime import datetime, timezone

        self.report = HealthReport(
            path=str(FIXTURES),
            timestamp=datetime.now(timezone.utc).isoformat(),
            files_scanned=files_scanned,
            todos=todos,
            smells=smells,
            summary=_build_summary(smells, todos),
        )

    def test_report_path_matches_input(self):
        assert str(FIXTURES) in self.report.path

    def test_report_timestamp_is_set(self):
        assert self.report.timestamp != ""

    def test_report_files_scanned_positive(self):
        assert self.report.files_scanned > 0

    def test_report_todos_is_list(self):
        assert isinstance(self.report.todos, list)

    def test_report_smells_is_list(self):
        assert isinstance(self.report.smells, list)

    def test_report_summary_has_correct_keys(self):
        assert set(self.report.summary.keys()) == {"high", "medium", "low", "todos"}

    def test_report_todos_count_matches_summary(self):
        assert self.report.summary["todos"] == len(self.report.todos)

    def test_report_high_count_matches_summary(self):
        expected = sum(1 for s in self.report.smells if s.severity == "high")
        assert self.report.summary["high"] == expected

    def test_report_can_be_serialized_to_dict(self):
        d = self.report.model_dump()
        assert isinstance(d, dict)
        assert "path" in d
        assert "timestamp" in d
        assert "files_scanned" in d
        assert "todos" in d
        assert "smells" in d
        assert "summary" in d


class TestState:
    """Tests for in-memory state store."""

    def test_set_and_get_last_report(self):
        from datetime import datetime, timezone

        report = HealthReport(
            path="/tmp/test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            files_scanned=1,
            todos=[],
            smells=[],
            summary={"high": 0, "medium": 0, "low": 0, "todos": 0},
        )
        set_last_report(report)
        stored = get_last_report()
        assert stored is not None
        assert stored["path"] == "/tmp/test"
        assert stored["files_scanned"] == 1
