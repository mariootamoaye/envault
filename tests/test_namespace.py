"""Tests for envault.namespace."""

import pytest
from envault.namespace import (
    make_key,
    split_key,
    list_namespaces,
    keys_in_namespace,
    get_namespace,
    delete_namespace,
    SEPARATOR,
)


class SimpleStore:
    def __init__(self, data: dict[str, str] | None = None):
        self._data: dict[str, str] = dict(data or {})

    def keys(self):
        return list(self._data.keys())

    def get(self, key: str):
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def unset(self, key: str):
        self._data.pop(key, None)


# --- make_key ---

def test_make_key_combines_with_separator():
    assert make_key("app", "secret") == f"APP{SEPARATOR}SECRET"


def test_make_key_uppercases_both_parts():
    assert make_key("myapp", "db_pass") == f"MYAPP{SEPARATOR}DB_PASS"


def test_make_key_empty_namespace_raises():
    with pytest.raises(ValueError, match="namespace"):
        make_key("", "KEY")


def test_make_key_empty_key_raises():
    with pytest.raises(ValueError, match="key"):
        make_key("NS", "")


# --- split_key ---

def test_split_key_returns_namespace_and_key():
    ns, key = split_key(f"APP{SEPARATOR}SECRET")
    assert ns == "APP"
    assert key == "SECRET"


def test_split_key_no_separator_raises():
    with pytest.raises(ValueError):
        split_key("NOSEPARATOR")


# --- list_namespaces ---

def test_list_namespaces_empty_store():
    store = SimpleStore()
    assert list_namespaces(store) == []


def test_list_namespaces_returns_unique_sorted():
    store = SimpleStore({f"APP{SEPARATOR}KEY": "v", f"DB{SEPARATOR}URL": "v", f"APP{SEPARATOR}TOKEN": "v"})
    assert list_namespaces(store) == ["APP", "DB"]


def test_list_namespaces_ignores_keys_without_separator():
    store = SimpleStore({"PLAIN_KEY": "v", f"NS{SEPARATOR}KEY": "v"})
    assert list_namespaces(store) == ["NS"]


# --- keys_in_namespace ---

def test_keys_in_namespace_returns_matching():
    store = SimpleStore({f"APP{SEPARATOR}A": "1", f"APP{SEPARATOR}B": "2", f"DB{SEPARATOR}URL": "3"})
    assert keys_in_namespace(store, "APP") == [f"APP{SEPARATOR}A", f"APP{SEPARATOR}B"]


def test_keys_in_namespace_empty_when_no_match():
    store = SimpleStore({f"DB{SEPARATOR}URL": "v"})
    assert keys_in_namespace(store, "APP") == []


# --- get_namespace ---

def test_get_namespace_returns_short_keys():
    store = SimpleStore({f"APP{SEPARATOR}SECRET": "abc", f"APP{SEPARATOR}TOKEN": "xyz"})
    result = get_namespace(store, "APP")
    assert result == {"SECRET": "abc", "TOKEN": "xyz"}


def test_get_namespace_empty_when_no_keys():
    store = SimpleStore()
    assert get_namespace(store, "APP") == {}


# --- delete_namespace ---

def test_delete_namespace_removes_all_keys():
    store = SimpleStore({f"APP{SEPARATOR}A": "1", f"APP{SEPARATOR}B": "2", f"DB{SEPARATOR}URL": "3"})
    count = delete_namespace(store, "APP")
    assert count == 2
    assert keys_in_namespace(store, "APP") == []
    assert keys_in_namespace(store, "DB") == [f"DB{SEPARATOR}URL"]


def test_delete_namespace_returns_zero_when_empty():
    store = SimpleStore()
    assert delete_namespace(store, "GHOST") == 0
