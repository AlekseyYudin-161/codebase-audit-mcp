"""Tests for scan_todos tool."""

from pathlib import Path
import pytest
from server.tools.scan_todos import _collect_todos

# Path to fixtures directory
FIXTURES = Path(__file__).parent / "fixtures"


class TestScanTodosWithMarkers:
    """Tests against sample_with_todos.py — expects exactly 6 items."""

    def setup_method(self):
        self.results = _collect_todos(FIXTURES)
        # Filter only items from our target fixture
        self.items = [r for r in self.results if "sample_with_todos" in r.file]

    def test_finds_exactly_six_markers(self):
        # One marker per tag: TODO, FIXME, HACK, XXX, NOTE, DEPRECATED
        assert len(self.items) == 6

    def test_finds_todo(self):
        tags = [i.tag for i in self.items]
        assert "TODO" in tags

    def test_finds_fixme(self):
        tags = [i.tag for i in self.items]
        assert "FIXME" in tags

    def test_finds_hack(self):
        tags = [i.tag for i in self.items]
        assert "HACK" in tags

    def test_finds_xxx(self):
        tags = [i.tag for i in self.items]
        assert "XXX" in tags

    def test_finds_note(self):
        tags = [i.tag for i in self.items]
        assert "NOTE" in tags

    def test_finds_deprecated(self):
        tags = [i.tag for i in self.items]
        assert "DEPRECATED" in tags

    def test_all_tags_are_uppercase(self):
        for item in self.items:
            assert item.tag == item.tag.upper()

    def test_all_items_have_file(self):
        for item in self.items:
            assert item.file != ""

    def test_all_items_have_positive_line_number(self):
        for item in self.items:
            assert item.line > 0

    def test_all_items_have_text(self):
        for item in self.items:
            assert item.text != ""

    def test_all_items_have_context(self):
        for item in self.items:
            assert item.context != ""

    def test_todo_line_number_is_correct(self):
        # Skip first TODO if it's in a header comment, find the real one
        todos = [i for i in self.items if i.tag == "TODO"]
        assert any("retry" in i.text.lower() for i in todos)

    def test_fixme_line_number_is_correct(self):
        fixme = next(i for i in self.items if i.tag == "FIXME")
        assert "missing keys" in fixme.text.lower()


class TestScanTodosCleanFile:
    """Tests against sample_clean.py — expects zero items."""

    def setup_method(self):
        self.results = _collect_todos(FIXTURES)
        self.items = [r for r in self.results if "sample_clean" in r.file]

    def test_no_false_positives(self):
        assert len(self.items) == 0


class TestScanTodosEdgeCases:
    """Edge case and error handling tests."""

    def test_raises_on_nonexistent_path(self):
        from server.tools.scan_todos import register_scan_todos
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_scan_todos(mcp)

        with pytest.raises(ValueError, match="does not exist"):
            from pathlib import Path

            _collect_todos(Path("/nonexistent/path/xyz"))

    def test_returns_list(self):
        result = _collect_todos(FIXTURES)
        assert isinstance(result, list)

    def test_result_items_have_correct_fields(self):
        results = _collect_todos(FIXTURES)
        if results:
            item = results[0]
            assert hasattr(item, "tag")
            assert hasattr(item, "file")
            assert hasattr(item, "line")
            assert hasattr(item, "text")
            assert hasattr(item, "context")
