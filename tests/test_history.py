"""Tests for envault.history."""
import pytest
from pathlib import Path
from envault.history import record_change, read_history, key_history, clear_history


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_read_returns_empty_when_no_file(vault_path):
    assert read_history(vault_path) == []


def test_record_creates_entry(vault_path):
    record_change(vault_path, "DB_URL", "set", None, "postgres://localhost/db")
    entries = read_history(vault_path)
    assert len(entries) == 1
    assert entries[0]["key"] == "DB_URL"
    assert entries[0]["action"] == "set"
    assert entries[0]["new"] == "postgres://localhost/db"
    assert entries[0]["old"] is None


def test_record_appends_multiple(vault_path):
    record_change(vault_path, "KEY", "set", None, "v1")
    record_change(vault_path, "KEY", "set", "v1", "v2")
    entries = read_history(vault_path)
    assert len(entries) == 2


def test_entry_has_timestamp(vault_path):
    record_change(vault_path, "X", "set", None, "1")
    entry = read_history(vault_path)[0]
    assert "ts" in entry
    assert "T" in entry["ts"]


def test_key_history_filters(vault_path):
    record_change(vault_path, "A", "set", None, "1")
    record_change(vault_path, "B", "set", None, "2")
    record_change(vault_path, "A", "unset", "1", None)
    result = key_history(vault_path, "A")
    assert len(result) == 2
    assert all(e["key"] == "A" for e in result)


def test_key_history_empty_for_unknown_key(vault_path):
    record_change(vault_path, "A", "set", None, "1")
    assert key_history(vault_path, "Z") == []


def test_clear_history(vault_path):
    record_change(vault_path, "A", "set", None, "1")
    clear_history(vault_path)
    assert read_history(vault_path) == []


def test_clear_history_no_file_is_noop(vault_path):
    clear_history(vault_path)  # should not raise
