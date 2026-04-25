"""Tests for envault.reorder."""

import pytest

from envault.reorder import move_key, reorder_store, sort_keys


# ---------------------------------------------------------------------------
# sort_keys
# ---------------------------------------------------------------------------

def _data():
    return {"ZEBRA": "1", "APPLE": "2", "MANGO": "3", "AB": "4"}


def test_sort_keys_alpha():
    result = sort_keys(_data(), mode="alpha")
    assert list(result.keys()) == ["AB", "APPLE", "MANGO", "ZEBRA"]


def test_sort_keys_alpha_desc():
    result = sort_keys(_data(), mode="alpha_desc")
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE", "AB"]


def test_sort_keys_length():
    result = sort_keys(_data(), mode="length")
    assert list(result.keys())[0] == "AB"
    assert list(result.keys())[-1] == "APPLE"


def test_sort_keys_length_desc():
    result = sort_keys(_data(), mode="length_desc")
    assert list(result.keys())[0] == "APPLE"
    assert list(result.keys())[-1] == "AB"


def test_sort_keys_preserves_values():
    result = sort_keys(_data(), mode="alpha")
    assert result["ZEBRA"] == "1"
    assert result["APPLE"] == "2"


def test_sort_keys_invalid_mode_raises():
    with pytest.raises(ValueError, match="Unknown sort mode"):
        sort_keys(_data(), mode="bogus")


def test_sort_keys_empty_dict():
    assert sort_keys({}) == {}


# ---------------------------------------------------------------------------
# move_key
# ---------------------------------------------------------------------------

def test_move_key_to_front():
    data = {"A": "1", "B": "2", "C": "3"}
    result = move_key(data, "C", 0)
    assert list(result.keys()) == ["C", "A", "B"]


def test_move_key_to_end():
    data = {"A": "1", "B": "2", "C": "3"}
    result = move_key(data, "A", 2)
    assert list(result.keys()) == ["B", "C", "A"]


def test_move_key_clamps_negative_position():
    data = {"A": "1", "B": "2", "C": "3"}
    result = move_key(data, "B", -99)
    assert list(result.keys())[0] == "B"


def test_move_key_clamps_overflow_position():
    data = {"A": "1", "B": "2", "C": "3"}
    result = move_key(data, "A", 999)
    assert list(result.keys())[-1] == "A"


def test_move_key_missing_key_raises():
    data = {"A": "1"}
    with pytest.raises(KeyError):
        move_key(data, "Z", 0)


# ---------------------------------------------------------------------------
# reorder_store  (uses a minimal fake store)
# ---------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, data):
        self._data = dict(data)

    def keys(self):
        return list(self._data.keys())

    def get(self, k):
        return self._data[k]

    def set(self, k, v):
        self._data[k] = v

    def unset(self, k):
        self._data.pop(k, None)


def test_reorder_store_returns_count():
    store = _FakeStore({"Z": "1", "A": "2", "M": "3"})
    count = reorder_store(store, mode="alpha")
    assert count == 3


def test_reorder_store_alpha_order():
    store = _FakeStore({"Z": "1", "A": "2", "M": "3"})
    reorder_store(store, mode="alpha")
    assert store.keys() == ["A", "M", "Z"]
