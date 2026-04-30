"""Tests for envault.inherit."""

from pathlib import Path

import pytest

from envault.store import VaultStore
from envault.inherit import resolve, resolve_all

PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _make_store(base_dir: Path, profile: str, data: dict) -> None:
    path = base_dir / f"{profile}.vault"
    store = VaultStore(path, PASSWORD)
    for k, v in data.items():
        store.set(k, v)
    store.save()


# ---------------------------------------------------------------------------
# resolve()
# ---------------------------------------------------------------------------

def test_resolve_finds_key_in_first_profile(vault_dir):
    _make_store(vault_dir, "prod", {"DB_URL": "postgres://prod"})
    result = resolve("DB_URL", ["prod"], PASSWORD, base_dir=vault_dir)
    assert result.found
    assert result.value == "postgres://prod"
    assert result.resolved_from == "prod"


def test_resolve_falls_back_to_later_profile(vault_dir):
    _make_store(vault_dir, "base", {"LOG_LEVEL": "info"})
    _make_store(vault_dir, "prod", {"DB_URL": "postgres://prod"})
    result = resolve("LOG_LEVEL", ["prod", "base"], PASSWORD, base_dir=vault_dir)
    assert result.found
    assert result.resolved_from == "base"
    assert result.value == "info"


def test_resolve_most_specific_wins(vault_dir):
    _make_store(vault_dir, "base", {"LOG_LEVEL": "info"})
    _make_store(vault_dir, "prod", {"LOG_LEVEL": "warning"})
    result = resolve("LOG_LEVEL", ["prod", "base"], PASSWORD, base_dir=vault_dir)
    assert result.resolved_from == "prod"
    assert result.value == "warning"


def test_resolve_returns_not_found_when_key_absent(vault_dir):
    _make_store(vault_dir, "base", {"OTHER": "x"})
    result = resolve("MISSING", ["base"], PASSWORD, base_dir=vault_dir)
    assert not result.found
    assert result.value is None
    assert result.resolved_from is None


def test_resolve_missing_profile_file_is_skipped(vault_dir):
    # "ghost" profile has no file; "base" does
    _make_store(vault_dir, "base", {"API_KEY": "abc"})
    result = resolve("API_KEY", ["ghost", "base"], PASSWORD, base_dir=vault_dir)
    assert result.found
    assert result.resolved_from == "base"


def test_resolve_records_full_chain(vault_dir):
    _make_store(vault_dir, "base", {"X": "1"})
    chain = ["prod", "staging", "base"]
    result = resolve("X", chain, PASSWORD, base_dir=vault_dir)
    assert result.chain == chain


# ---------------------------------------------------------------------------
# resolve_all()
# ---------------------------------------------------------------------------

def test_resolve_all_merges_keys(vault_dir):
    _make_store(vault_dir, "base", {"LOG_LEVEL": "info", "TIMEOUT": "30"})
    _make_store(vault_dir, "prod", {"DB_URL": "postgres://prod"})
    merged = resolve_all(["prod", "base"], PASSWORD, base_dir=vault_dir)
    assert set(merged.keys()) == {"LOG_LEVEL", "TIMEOUT", "DB_URL"}


def test_resolve_all_specific_profile_wins(vault_dir):
    _make_store(vault_dir, "base", {"LOG_LEVEL": "info"})
    _make_store(vault_dir, "prod", {"LOG_LEVEL": "error"})
    merged = resolve_all(["prod", "base"], PASSWORD, base_dir=vault_dir)
    assert merged["LOG_LEVEL"].resolved_from == "prod"
    assert merged["LOG_LEVEL"].value == "error"


def test_resolve_all_empty_chain_returns_empty(vault_dir):
    merged = resolve_all([], PASSWORD, base_dir=vault_dir)
    assert merged == {}
