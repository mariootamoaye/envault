"""Tests for envault.search."""
from __future__ import annotations

import pytest

from envault.search import search_keys, search_values


@pytest.fixture()
def vault(tmp_path):
    from envault.store import VaultStore

    v = VaultStore(tmp_path / "vault.json")
    password = "testpass"
    v.set("DB_HOST", "localhost", password)
    v.set("DB_PASSWORD", "s3cr3t", password)
    v.set("API_KEY", "abc123", password)
    v.set("API_SECRET", "xyz789", password)
    v.set("DEBUG", "true", password)
    return v, password


def test_search_keys_exact_prefix(vault):
    store, pw = vault
    results = search_keys(store, pw, "DB_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_search_keys_wildcard_middle(vault):
    store, pw = vault
    results = search_keys(store, pw, "*SECRET*")
    assert "API_SECRET" in results
    assert "DB_PASSWORD" not in results


def test_search_keys_no_match(vault):
    store, pw = vault
    results = search_keys(store, pw, "MISSING_*")
    assert results == {}


def test_search_keys_case_insensitive_default(vault):
    store, pw = vault
    results = search_keys(store, pw, "db_*")
    assert set(results.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_search_keys_case_sensitive_no_match(vault):
    store, pw = vault
    results = search_keys(store, pw, "db_*", case_sensitive=True)
    assert results == {}


def test_search_keys_values_are_decrypted(vault):
    store, pw = vault
    results = search_keys(store, pw, "DEBUG")
    assert results["DEBUG"] == "true"


def test_search_values_finds_substring(vault):
    store, pw = vault
    results = search_values(store, pw, "123")
    assert "API_KEY" in results
    assert results["API_KEY"] == "abc123"


def test_search_values_case_insensitive_default(vault):
    store, pw = vault
    results = search_values(store, pw, "S3CR3T")
    assert "DB_PASSWORD" in results


def test_search_values_case_sensitive(vault):
    store, pw = vault
    results = search_values(store, pw, "S3CR3T", case_sensitive=True)
    assert "DB_PASSWORD" not in results
    results2 = search_values(store, pw, "s3cr3t", case_sensitive=True)
    assert "DB_PASSWORD" in results2


def test_search_values_no_match(vault):
    store, pw = vault
    results = search_values(store, pw, "NOPE_NOT_HERE")
    assert results == {}
