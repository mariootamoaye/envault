"""Tests for envault.store.VaultStore."""

from __future__ import annotations

import pytest

from envault.store import VaultStore

PASSWORD = "hunter2"


@pytest.fixture()
def vault(tmp_path):
    return VaultStore(path=tmp_path / ".envault")


def test_load_returns_empty_when_no_file(vault):
    assert vault.load(PASSWORD) == {}


def test_save_and_load_roundtrip(vault):
    data = {"DB_URL": "postgres://localhost/test", "SECRET": "abc123"}
    vault.save(data, PASSWORD)
    assert vault.load(PASSWORD) == data


def test_set_adds_variable(vault):
    vault.set("FOO", "bar", PASSWORD)
    assert vault.load(PASSWORD)["FOO"] == "bar"


def test_set_updates_existing_variable(vault):
    vault.set("FOO", "bar", PASSWORD)
    vault.set("FOO", "baz", PASSWORD)
    assert vault.load(PASSWORD)["FOO"] == "baz"


def test_unset_removes_variable(vault):
    vault.set("FOO", "bar", PASSWORD)
    removed = vault.unset("FOO", PASSWORD)
    assert removed is True
    assert "FOO" not in vault.load(PASSWORD)


def test_unset_returns_false_for_missing_key(vault):
    assert vault.unset("MISSING", PASSWORD) is False


def test_list_keys_returns_sorted(vault):
    vault.save({"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}, PASSWORD)
    assert vault.list_keys(PASSWORD) == ["APPLE", "MANGO", "ZEBRA"]


def test_wrong_password_raises_on_load(vault):
    vault.set("KEY", "value", PASSWORD)
    with pytest.raises(Exception):
        vault.load("wrongpassword")
