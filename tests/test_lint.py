"""Tests for envault.lint."""
import pytest
from envault.lint import lint, lint_keys, lint_values, LintIssue


def test_valid_keys_produce_no_issues():
    issues = lint_keys(["DATABASE_URL", "API_KEY", "PORT"])
    assert issues == []


def test_lowercase_key_produces_warning():
    issues = lint_keys(["database_url"])
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "database_url" in issues[0].key


def test_key_with_hyphen_produces_warning():
    issues = lint_keys(["MY-KEY"])
    assert any(i.severity == "warning" for i in issues)


def test_empty_key_produces_error():
    issues = lint_keys([""])
    assert len(issues) == 1
    assert issues[0].severity == "error"


def test_leading_underscore_produces_warning():
    issues = lint_keys(["_INTERNAL"])
    # _INTERNAL matches regex but leading _ is flagged
    severities = [i.severity for i in issues]
    assert "warning" in severities


def test_empty_value_produces_warning():
    issues = lint_values({"API_KEY": ""})
    assert len(issues) == 1
    assert "empty" in issues[0].message.lower()


def test_long_value_produces_warning():
    issues = lint_values({"BIG": "x" * 5000})
    assert any("long" in i.message.lower() for i in issues)


def test_newline_in_value_produces_warning():
    issues = lint_values({"MULTI": "line1\nline2"})
    assert any("newline" in i.message.lower() for i in issues)


def test_clean_store_no_issues():
    issues = lint({"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"})
    assert issues == []


def test_lint_combines_key_and_value_issues():
    issues = lint({"bad-key": ""})
    severities = {i.severity for i in issues}
    assert "warning" in severities
    assert len(issues) >= 2


def test_lint_issue_str_format():
    issue = LintIssue(key="FOO", severity="error", message="Something wrong")
    s = str(issue)
    assert "ERROR" in s
    assert "FOO" in s
    assert "Something wrong" in s
