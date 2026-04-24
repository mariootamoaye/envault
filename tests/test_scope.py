"""Tests for envault.scope."""
from pathlib import Path

import pytest

from envault.scope import (
    filter_by_scope,
    keys_in_scope,
    list_scopes,
    load_scopes,
    remove_scope,
    set_scope,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_scopes(vault_path) == {}


def test_set_scope_creates_entry(vault_path):
    set_scope(vault_path, "API_KEY", "prod")
    assert load_scopes(vault_path) == {"API_KEY": "prod"}


def test_set_scope_overwrites_existing(vault_path):
    set_scope(vault_path, "API_KEY", "prod")
    set_scope(vault_path, "API_KEY", "ci")
    assert load_scopes(vault_path)["API_KEY"] == "ci"


def test_set_scope_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="key"):
        set_scope(vault_path, "", "prod")


def test_set_scope_empty_scope_raises(vault_path):
    with pytest.raises(ValueError, match="scope"):
        set_scope(vault_path, "KEY", "")


def test_remove_scope_returns_true_when_found(vault_path):
    set_scope(vault_path, "KEY", "prod")
    assert remove_scope(vault_path, "KEY") is True
    assert load_scopes(vault_path) == {}


def test_remove_scope_returns_false_when_missing(vault_path):
    assert remove_scope(vault_path, "MISSING") is False


def test_keys_in_scope(vault_path):
    set_scope(vault_path, "A", "prod")
    set_scope(vault_path, "B", "ci")
    set_scope(vault_path, "C", "prod")
    assert sorted(keys_in_scope(vault_path, "prod")) == ["A", "C"]
    assert keys_in_scope(vault_path, "ci") == ["B"]


def test_list_scopes_returns_unique_sorted(vault_path):
    set_scope(vault_path, "A", "prod")
    set_scope(vault_path, "B", "ci")
    set_scope(vault_path, "C", "prod")
    assert list_scopes(vault_path) == ["ci", "prod"]


def test_filter_by_scope_none_returns_all(vault_path):
    data = {"A": "1", "B": "2"}
    assert filter_by_scope(data, vault_path, None) == data


def test_filter_by_scope_filters_correctly(vault_path):
    set_scope(vault_path, "A", "prod")
    data = {"A": "1", "B": "2", "C": "3"}
    result = filter_by_scope(data, vault_path, "prod")
    assert result == {"A": "1"}


def test_filter_by_scope_unknown_scope_returns_empty(vault_path):
    data = {"A": "1"}
    assert filter_by_scope(data, vault_path, "ghost") == {}
