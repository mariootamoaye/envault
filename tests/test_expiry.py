"""Tests for envault.expiry."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.expiry import (
    expired_keys,
    get_expiry,
    is_expired,
    load_expiry,
    purge_expired,
    remove_expiry,
    set_expiry,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def _future(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(days=days)


def test_load_returns_empty_when_no_file(vault_path):
    assert load_expiry(vault_path) == {}


def test_set_expiry_persists(vault_path):
    exp = _future()
    set_expiry(vault_path, "MY_KEY", exp)
    data = load_expiry(vault_path)
    assert "MY_KEY" in data


def test_get_expiry_returns_datetime(vault_path):
    exp = _future()
    set_expiry(vault_path, "MY_KEY", exp)
    result = get_expiry(vault_path, "MY_KEY")
    assert isinstance(result, datetime)
    assert abs((result - exp).total_seconds()) < 1


def test_get_expiry_returns_none_when_unset(vault_path):
    assert get_expiry(vault_path, "MISSING") is None


def test_is_expired_false_for_future(vault_path):
    set_expiry(vault_path, "K", _future())
    assert is_expired(vault_path, "K") is False


def test_is_expired_true_for_past(vault_path):
    set_expiry(vault_path, "K", _past())
    assert is_expired(vault_path, "K") is True


def test_is_expired_false_when_no_expiry(vault_path):
    assert is_expired(vault_path, "NOEXPIRY") is False


def test_remove_expiry_clears_key(vault_path):
    set_expiry(vault_path, "K", _future())
    remove_expiry(vault_path, "K")
    assert get_expiry(vault_path, "K") is None


def test_expired_keys_returns_only_past(vault_path):
    set_expiry(vault_path, "OLD", _past())
    set_expiry(vault_path, "NEW", _future())
    assert expired_keys(vault_path) == ["OLD"]


def test_purge_expired_removes_from_store(vault_path):
    class FakeStore:
        def __init__(self):
            self._data = {"OLD": "v1", "NEW": "v2"}

        def unset(self, key):
            self._data.pop(key, None)

    store = FakeStore()
    set_expiry(vault_path, "OLD", _past())
    set_expiry(vault_path, "NEW", _future())
    purged = purge_expired(vault_path, store)
    assert purged == ["OLD"]
    assert "OLD" not in store._data
    assert "NEW" in store._data
    assert get_expiry(vault_path, "OLD") is None
