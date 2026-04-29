"""Tests for envault.promote."""

import pytest

from envault.store import VaultStore
from envault.promote import promote, PromoteResult


PASSWORD = "test-secret"


@pytest.fixture()
def src_store(tmp_path):
    store = VaultStore(tmp_path / "src.vault")
    store.set("DB_HOST", "localhost", PASSWORD)
    store.set("DB_PORT", "5432", PASSWORD)
    store.set("API_KEY", "abc123", PASSWORD)
    return store


@pytest.fixture()
def dst_store(tmp_path):
    return VaultStore(tmp_path / "dst.vault")


def test_promote_all_keys(src_store, dst_store):
    result = promote(src_store, dst_store, PASSWORD)
    assert set(result.promoted) == {"DB_HOST", "DB_PORT", "API_KEY"}
    assert result.skipped == []
    assert result.overwritten == []


def test_promote_specific_keys(src_store, dst_store):
    result = promote(src_store, dst_store, PASSWORD, keys=["DB_HOST"])
    assert result.promoted == ["DB_HOST"]
    assert "DB_PORT" not in result.promoted
    assert dst_store.get("DB_HOST") == "localhost"


def test_promote_skips_missing_key(src_store, dst_store):
    result = promote(src_store, dst_store, PASSWORD, keys=["NONEXISTENT"])
    assert result.promoted == []
    assert "NONEXISTENT" in result.skipped


def test_promote_no_overwrite_by_default(src_store, dst_store):
    dst_store.set("DB_HOST", "prod-host", PASSWORD)
    result = promote(src_store, dst_store, PASSWORD)
    assert "DB_HOST" in result.skipped
    assert dst_store.get("DB_HOST") == "prod-host"


def test_promote_overwrite_flag(src_store, dst_store):
    dst_store.set("DB_HOST", "prod-host", PASSWORD)
    result = promote(src_store, dst_store, PASSWORD, overwrite=True)
    assert "DB_HOST" in result.overwritten
    assert dst_store.get("DB_HOST") == "localhost"


def test_promote_dry_run_makes_no_changes(src_store, dst_store):
    result = promote(src_store, dst_store, PASSWORD, dry_run=True)
    assert len(result.promoted) == 3
    assert dst_store.keys() == []


def test_promote_result_total(src_store, dst_store):
    dst_store.set("DB_HOST", "old", PASSWORD)
    result = promote(src_store, dst_store, PASSWORD, overwrite=True)
    assert result.total == len(result.promoted) + len(result.overwritten)
