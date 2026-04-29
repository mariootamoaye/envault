"""Tests for envault.archive."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.archive import (
    archive_key,
    list_archived,
    load_archive,
    purge_archive,
    restore_key,
)


class SimpleStore:
    def __init__(self, data: dict | None = None):
        self._data: dict[str, str] = data or {}
        self._saved = False

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def unset(self, key: str):
        self._data.pop(key, None)

    def save(self):
        self._saved = True

    def keys(self):
        return list(self._data.keys())


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_archive(vault_path) == {}


def test_archive_key_moves_to_archive(vault_path):
    store = SimpleStore({"DB_URL": "postgres://localhost/dev"})
    result = archive_key(vault_path, store, "DB_URL")
    assert result is True
    assert store.get("DB_URL") is None
    assert load_archive(vault_path)["DB_URL"] == "postgres://localhost/dev"


def test_archive_key_returns_false_when_missing(vault_path):
    store = SimpleStore()
    assert archive_key(vault_path, store, "MISSING") is False


def test_archive_key_triggers_save(vault_path):
    store = SimpleStore({"X": "1"})
    archive_key(vault_path, store, "X")
    assert store._saved is True


def test_restore_key_moves_back_to_store(vault_path):
    store = SimpleStore({"DB_URL": "postgres://localhost/dev"})
    archive_key(vault_path, store, "DB_URL")
    result = restore_key(vault_path, store, "DB_URL")
    assert result is True
    assert store.get("DB_URL") == "postgres://localhost/dev"
    assert "DB_URL" not in load_archive(vault_path)


def test_restore_key_returns_false_when_not_archived(vault_path):
    store = SimpleStore()
    assert restore_key(vault_path, store, "GHOST") is False


def test_list_archived_sorted(vault_path):
    store = SimpleStore({"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"})
    for k in ["ZEBRA", "ALPHA", "MIDDLE"]:
        archive_key(vault_path, store, k)
    assert list_archived(vault_path) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_purge_specific_key(vault_path):
    store = SimpleStore({"A": "1", "B": "2"})
    archive_key(vault_path, store, "A")
    archive_key(vault_path, store, "B")
    count = purge_archive(vault_path, "A")
    assert count == 1
    remaining = load_archive(vault_path)
    assert "A" not in remaining
    assert "B" in remaining


def test_purge_all_keys(vault_path):
    store = SimpleStore({"A": "1", "B": "2"})
    archive_key(vault_path, store, "A")
    archive_key(vault_path, store, "B")
    count = purge_archive(vault_path)
    assert count == 2
    assert load_archive(vault_path) == {}


def test_purge_missing_key_returns_zero(vault_path):
    assert purge_archive(vault_path, "NOPE") == 0
