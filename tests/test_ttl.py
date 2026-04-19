"""Tests for envault.ttl."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import pytest

from envault.ttl import (
    set_ttl,
    get_expiry,
    is_expired,
    purge_expired,
    clear_ttl,
    TTL_META_PREFIX,
)


class FakeStore:
    def __init__(self):
        self._data: dict[str, str] = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key)

    def unset(self, key):
        if key not in self._data:
            raise KeyError(key)
        del self._data[key]

    def list(self):
        return list(self._data.keys())


@pytest.fixture
def store():
    s = FakeStore()
    s.set("API_KEY", "abc123")
    s.set("DB_PASS", "secret")
    return s


def test_set_ttl_stores_meta_key(store):
    set_ttl(store, "API_KEY", 3600)
    assert store.get(TTL_META_PREFIX + "API_KEY") is not None


def test_get_expiry_returns_none_without_ttl(store):
    assert get_expiry(store, "API_KEY") is None


def test_get_expiry_returns_datetime(store):
    set_ttl(store, "API_KEY", 3600)
    expiry = get_expiry(store, "API_KEY")
    assert isinstance(expiry, datetime)
    assert expiry.tzinfo == timezone.utc


def test_is_expired_false_for_future(store):
    set_ttl(store, "API_KEY", 3600)
    assert is_expired(store, "API_KEY") is False


def test_is_expired_true_for_past(store):
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    store.set(TTL_META_PREFIX + "API_KEY", past.isoformat())
    assert is_expired(store, "API_KEY") is True


def test_is_expired_false_without_ttl(store):
    assert is_expired(store, "DB_PASS") is False


def test_purge_expired_removes_expired_key(store):
    past = datetime.now(timezone.utc) - timedelta(seconds=10)
    store.set(TTL_META_PREFIX + "API_KEY", past.isoformat())
    purged = purge_expired(store)
    assert "API_KEY" in purged
    assert store.get("API_KEY") is None
    assert store.get(TTL_META_PREFIX + "API_KEY") is None


def test_purge_expired_leaves_valid_key(store):
    set_ttl(store, "API_KEY", 3600)
    purged = purge_expired(store)
    assert "API_KEY" not in purged
    assert store.get("API_KEY") == "abc123"


def test_purge_expired_returns_empty_when_none_expired(store):
    assert purge_expired(store) == []


def test_clear_ttl_removes_meta(store):
    set_ttl(store, "API_KEY", 3600)
    clear_ttl(store, "API_KEY")
    assert get_expiry(store, "API_KEY") is None


def test_clear_ttl_no_error_when_no_ttl(store):
    clear_ttl(store, "API_KEY")  # should not raise
