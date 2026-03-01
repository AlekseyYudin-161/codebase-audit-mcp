"""Tests for find_code_smells tool."""

from pathlib import Path

import pytest

from server.tools.find_code_smells import _collect_smells

FIXTURES = Path(__file__).parent / "fixtures"


class TestFindSmellsWithProblems:
    """Tests against sample_with_smells.py — expects all categories present."""

    def setup_method(self):
        all_results = _collect_smells(FIXTURES)
        self.items = [r for r in all_results if "sample_with_smells" in r.file]
        self.categories = [i.category for i in self.items]
        self.severities = [i.severity for i in self.items]

    def test_finds_secrets(self):
        assert "secret" in self.categories

    def test_finds_dangerous_calls(self):
        assert "dangerous_call" in self.categories

    def test_finds_long_function(self):
        assert "long_function" in self.categories

    def test_finds_high_complexity(self):
        assert "high_complexity" in self.categories

    def test_finds_commented_block(self):
        assert "commented_block" in self.categories

    def test_secrets_are_high_severity(self):
        secrets = [i for i in self.items if i.category == "secret"]
        assert all(s.severity == "high" for s in secrets)

    def test_dangerous_calls_are_high_severity(self):
        dangerous = [i for i in self.items if i.category == "dangerous_call"]
        assert all(d.severity == "high" for d in dangerous)

    def test_long_function_is_medium_severity(self):
        long_fns = [i for i in self.items if i.category == "long_function"]
        assert all(f.severity == "medium" for f in long_fns)

    def test_high_complexity_is_high_severity(self):
        complex_fns = [i for i in self.items if i.category == "high_complexity"]
        assert all(c.severity == "high" for c in complex_fns)

    def test_commented_block_is_low_severity(self):
        blocks = [i for i in self.items if i.category == "commented_block"]
        assert all(b.severity == "low" for b in blocks)

    def test_finds_password_secret(self):
        secrets = [i for i in self.items if i.category == "secret"]
        snippets = [s.snippet for s in secrets]
        assert any("password" in s.lower() for s in snippets)

    def test_finds_api_key_secret(self):
        secrets = [i for i in self.items if i.category == "secret"]
        snippets = [s.snippet for s in secrets]
        assert any("api_key" in s.lower() for s in snippets)

    def test_finds_eval(self):
        dangerous = [i for i in self.items if i.category == "dangerous_call"]
        descriptions = [d.description for d in dangerous]
        assert any("eval" in d for d in descriptions)

    def test_finds_exec(self):
        dangerous = [i for i in self.items if i.category == "dangerous_call"]
        descriptions = [d.description for d in dangerous]
        assert any("exec" in d for d in descriptions)

    def test_all_items_have_positive_line(self):
        for item in self.items:
            assert item.line > 0

    def test_all_items_have_file(self):
        for item in self.items:
            assert item.file != ""

    def test_all_items_have_description(self):
        for item in self.items:
            assert item.description != ""

    def test_severity_values_are_valid(self):
        valid = {"high", "medium", "low"}
        for item in self.items:
            assert item.severity in valid


class TestFindSmellsCleanFile:
    """Tests against sample_clean.py — expects zero smells."""

    def setup_method(self):
        all_results = _collect_smells(FIXTURES)
        self.items = [r for r in all_results if "sample_clean" in r.file]

    def test_no_secrets_in_clean_file(self):
        secrets = [i for i in self.items if i.category == "secret"]
        assert len(secrets) == 0

    def test_no_dangerous_calls_in_clean_file(self):
        dangerous = [i for i in self.items if i.category == "dangerous_call"]
        assert len(dangerous) == 0

    def test_no_long_functions_in_clean_file(self):
        long_fns = [i for i in self.items if i.category == "long_function"]
        assert len(long_fns) == 0

    def test_no_high_complexity_in_clean_file(self):
        complex_fns = [i for i in self.items if i.category == "high_complexity"]
        assert len(complex_fns) == 0


class TestFindSmellsEdgeCases:
    """Edge case tests."""

    def test_returns_list(self):
        result = _collect_smells(FIXTURES)
        assert isinstance(result, list)

    def test_result_items_have_correct_fields(self):
        results = _collect_smells(FIXTURES)
        if results:
            item = results[0]
            assert hasattr(item, "category")
            assert hasattr(item, "severity")
            assert hasattr(item, "file")
            assert hasattr(item, "line")
            assert hasattr(item, "description")
            assert hasattr(item, "snippet")
