"""Tests for envault.snapshot"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
)


PASSWORD = "s3cr3t"


@pytest.fixture()
def store(tmp_path):
    from envault.store import VaultStore
    s = VaultStore(str(tmp_path / "vault.json"))
    s.set("FOO", "bar", PASSWORD)
    s.set("BAZ", "qux", PASSWORD)
    s.save()
    return s


def test_create_snapshot_returns_filename(store):
    name = create_snapshot(store, PASSWORD, label="initial")
    assert name.endswith(".json")


def test_list_snapshots_empty(store):
    assert list_snapshots(store) == []


def test_list_snapshots_shows_entry(store):
    create_snapshot(store, PASSWORD, label="v1")
    snaps = list_snapshots(store)
    assert len(snaps) == 1
    assert snaps[0]["keys"] == 2
    assert snaps[0]["label"] == "v1"


def test_list_snapshots_sorted_newest_first(store):
    create_snapshot(store, PASSWORD, label="first")
    store.set("NEW", "val", PASSWORD)
    store.save()
    create_snapshot(store, PASSWORD, label="second")
    snaps = list_snapshots(store)
    assert snaps[0]["label"] == "second"


def test_restore_snapshot_repopulates_keys(store, tmp_path):
    from envault.store import VaultStore
    name = create_snapshot(store, PASSWORD)
    empty = VaultStore(str(tmp_path / "vault2.json"))
    count = restore_snapshot(empty, PASSWORD, name)
    assert count == 2
    assert empty.get("FOO", PASSWORD) == "bar"
    assert empty.get("BAZ", PASSWORD) == "qux"


def test_delete_snapshot_removes_file(store):
    name = create_snapshot(store, PASSWORD)
    assert delete_snapshot(store, name) is True
    assert list_snapshots(store) == []


def test_delete_snapshot_missing_returns_false(store):
    assert delete_snapshot(store, "nonexistent.json") is False
