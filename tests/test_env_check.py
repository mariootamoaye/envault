"""Tests for envault.env_check."""
import os
import pytest
from envault.env_check import check_env, format_check, CheckResult


@pytest.fixture
def vault_data():
    return {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}


def test_missing_key(vault_data, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    results = {r.key: r for r in check_env(vault_data)}
    assert results["API_KEY"].status() == "missing"
    assert results["API_KEY"].in_env is False


def test_matching_key(vault_data, monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    results = {r.key: r for r in check_env({"API_KEY": "secret123"})}
    assert results["API_KEY"].status() == "ok"
    assert results["API_KEY"].match is True


def test_mismatched_key(monkeypatch):
    monkeypatch.setenv("PORT", "9999")
    results = {r.key: r for r in check_env({"PORT": "8080"})}
    assert results["PORT"].status() == "mismatch"
    assert results["PORT"].in_env is True
    assert results["PORT"].match is False


def test_check_result_str():
    r = CheckResult(key="FOO", in_vault=True, in_env=False, match=False)
    assert "FOO" in str(r)
    assert "missing" in str(r)


def test_format_check_shows_all_by_default(monkeypatch):
    monkeypatch.setenv("A", "1")
    monkeypatch.delenv("B", raising=False)
    results = check_env({"A": "1", "B": "2"})
    out = format_check(results)
    assert "A" in out
    assert "B" in out


def test_format_check_hides_ok(monkeypatch):
    monkeypatch.setenv("A", "1")
    monkeypatch.delenv("B", raising=False)
    results = check_env({"A": "1", "B": "2"})
    out = format_check(results, show_ok=False)
    assert "A" not in out
    assert "B" in out


def test_empty_vault():
    results = check_env({})
    assert results == []
    assert format_check(results) == ""
