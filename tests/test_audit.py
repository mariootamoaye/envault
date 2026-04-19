"""Tests for envault.audit."""
import pytest
from pathlib import Path
from envault.audit import record, read, clear


@pytest.fixture()
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.log"


def test_read_returns_empty_when_no_file(log_path):
    assert read(path=log_path) == []


def test_record_creates_file(log_path):
    record("set", key="FOO", profile="default", path=log_path)
    assert log_path.exists()


def test_record_entry_fields(log_path):
    record("set", key="BAR", profile="prod", path=log_path)
    entries = read(path=log_path)
    assert len(entries) == 1
    e = entries[0]
    assert e["action"] == "set"
    assert e["key"] == "BAR"
    assert e["profile"] == "prod"
    assert "ts" in e


def test_record_without_key(log_path):
    record("list", profile="default", path=log_path)
    entries = read(path=log_path)
    assert "key" not in entries[0]


def test_multiple_records_appended(log_path):
    record("set", key="A", path=log_path)
    record("set", key="B", path=log_path)
    record("unset", key="A", path=log_path)
    entries = read(path=log_path)
    assert len(entries) == 3
    assert entries[2]["action"] == "unset"


def test_clear_removes_file(log_path):
    record("set", key="X", path=log_path)
    clear(path=log_path)
    assert not log_path.exists()


def test_clear_noop_when_no_file(log_path):
    clear(path=log_path)  # should not raise
