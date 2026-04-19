"""Tests for envault.tags."""
import pytest
from unittest.mock import MagicMock

from envault.tags import (
    set_tags, get_tags, remove_tags, keys_by_tag, all_tags, META_PREFIX
)


class SimpleStore:
    def __init__(self):
        self._data: dict[str, str] = {}

    def set(self, k, v):
        self._data[k] = v

    def get(self, k):
        return self._data.get(k)

    def unset(self, k):
        if k not in self._data:
            raise KeyError(k)
        del self._data[k]

    def keys(self):
        return list(self._data.keys())


@pytest.fixture
def store():
    return SimpleStore()


def test_set_and_get_tags(store):
    set_tags(store, "DB_URL", ["db", "prod"])
    tags = get_tags(store, "DB_URL")
    assert "db" in tags
    assert "prod" in tags


def test_get_tags_no_entry(store):
    assert get_tags(store, "MISSING") == []


def test_tags_are_deduplicated(store):
    set_tags(store, "KEY", ["a", "a", "b"])
    assert get_tags(store, "KEY").count("a") == 1


def test_tags_sorted(store):
    set_tags(store, "KEY", ["z", "a", "m"])
    assert get_tags(store, "KEY") == ["a", "m", "z"]


def test_remove_tags(store):
    set_tags(store, "KEY", ["x"])
    remove_tags(store, "KEY")
    assert get_tags(store, "KEY") == []


def test_remove_tags_missing_is_noop(store):
    remove_tags(store, "NONEXISTENT")  # should not raise


def test_keys_by_tag(store):
    store.set("DB_URL", "x")
    store.set("API_KEY", "y")
    store.set("PORT", "z")
    set_tags(store, "DB_URL", ["infra"])
    set_tags(store, "API_KEY", ["infra", "secret"])
    set_tags(store, "PORT", ["network"])
    assert keys_by_tag(store, "infra") == ["API_KEY", "DB_URL"]
    assert keys_by_tag(store, "secret") == ["API_KEY"]
    assert keys_by_tag(store, "missing") == []


def test_all_tags(store):
    store.set("A", "1")
    store.set("B", "2")
    set_tags(store, "A", ["t1"])
    result = all_tags(store)
    assert "A" in result
    assert "B" not in result


def test_meta_keys_excluded_from_keys_by_tag(store):
    store.set("REAL", "v")
    set_tags(store, "REAL", ["web"])
    # meta key itself should not appear in keys_by_tag results
    assert all(not k.startswith(META_PREFIX) for k in keys_by_tag(store, "web"))
