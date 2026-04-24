"""Tests for envault.blame."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.blame import (
    format_blame,
    get_blame,
    load_blame,
    record_blame,
    remove_blame,
    save_blame,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_blame(vault_path) == {}


def test_record_blame_creates_entry(vault_path):
    entry = record_blame(vault_path, "MY_KEY", user="alice", host="box")
    assert entry["user"] == "alice"
    assert entry["host"] == "box"
    assert "timestamp" in entry


def test_record_blame_persists(vault_path):
    record_blame(vault_path, "MY_KEY", user="bob", host="srv")
    data = load_blame(vault_path)
    assert "MY_KEY" in data
    assert data["MY_KEY"]["user"] == "bob"


def test_record_blame_overwrites_existing(vault_path):
    record_blame(vault_path, "KEY", user="alice", host="a")
    record_blame(vault_path, "KEY", user="bob", host="b")
    entry = get_blame(vault_path, "KEY")
    assert entry["user"] == "bob"


def test_record_blame_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        record_blame(vault_path, "", user="alice", host="box")


def test_get_blame_returns_none_for_unknown_key(vault_path):
    assert get_blame(vault_path, "MISSING") is None


def test_get_blame_returns_entry(vault_path):
    record_blame(vault_path, "K", user="carol", host="h")
    entry = get_blame(vault_path, "K")
    assert entry is not None
    assert entry["user"] == "carol"


def test_remove_blame_returns_true_when_exists(vault_path):
    record_blame(vault_path, "K", user="u", host="h")
    assert remove_blame(vault_path, "K") is True
    assert get_blame(vault_path, "K") is None


def test_remove_blame_returns_false_when_missing(vault_path):
    assert remove_blame(vault_path, "NOPE") is False


def test_save_and_load_roundtrip(vault_path):
    payload = {"A": {"user": "x", "host": "y", "timestamp": "2024-01-01T00:00:00+00:00"}}
    save_blame(vault_path, payload)
    assert load_blame(vault_path) == payload


def test_format_blame_returns_string(vault_path):
    record_blame(vault_path, "K", user="dave", host="laptop")
    entry = get_blame(vault_path, "K")
    result = format_blame(entry)
    assert "dave" in result
    assert "laptop" in result


def test_record_blame_uses_env_user(vault_path, monkeypatch):
    monkeypatch.setenv("USER", "env_user")
    entry = record_blame(vault_path, "K", host="h")
    assert entry["user"] == "env_user"
