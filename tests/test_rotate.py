"""Tests for envault.rotate."""

from __future__ import annotations

import pytest

from envault.store import VaultStore
from envault.rotate import rotate_password


@pytest.fixture()
def populated_vault(tmp_path):
    path = tmp_path / "vault.json"
    store = VaultStore(path, "old-pass")
    store.load()
    store.set("KEY1", "value1")
    store.set("KEY2", "value2")
    store.save()
    return path


def test_rotate_returns_key_count(populated_vault):
    count = rotate_password(populated_vault, "old-pass", "new-pass")
    assert count == 2


def test_rotate_new_password_decrypts(populated_vault):
    rotate_password(populated_vault, "old-pass", "new-pass")
    store = VaultStore(populated_vault, "new-pass")
    store.load()
    assert store.get("KEY1") == "value1"
    assert store.get("KEY2") == "value2"


def test_rotate_old_password_no_longer_works(populated_vault):
    rotate_password(populated_vault, "old-pass", "new-pass")
    store = VaultStore(populated_vault, "old-pass")
    store.load()
    with pytest.raises(Exception):
        store.get("KEY1")


def test_rotate_empty_vault(tmp_path):
    path = tmp_path / "vault.json"
    store = VaultStore(path, "old-pass")
    store.load()
    store.save()
    count = rotate_password(path, "old-pass", "new-pass")
    assert count == 0


def test_rotate_wrong_old_password_raises(populated_vault):
    with pytest.raises(Exception):
        rotate_password(populated_vault, "wrong-pass", "new-pass")
