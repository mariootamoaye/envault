"""Tests for envault.deprecate."""

import pytest
from pathlib import Path

from envault.deprecate import (
    load_deprecated,
    mark_deprecated,
    unmark_deprecated,
    is_deprecated,
    deprecation_warning,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault" / ".envault"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_deprecated(vault_path) == {}


def test_mark_creates_entry(vault_path):
    mark_deprecated(vault_path, "OLD_KEY")
    data = load_deprecated(vault_path)
    assert "OLD_KEY" in data


def test_mark_stores_reason_and_replacement(vault_path):
    mark_deprecated(vault_path, "DB_PASS", reason="Renamed", replacement="DB_PASSWORD")
    data = load_deprecated(vault_path)
    assert data["DB_PASS"]["reason"] == "Renamed"
    assert data["DB_PASS"]["replacement"] == "DB_PASSWORD"


def test_mark_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        mark_deprecated(vault_path, "")


def test_mark_overwrites_existing(vault_path):
    mark_deprecated(vault_path, "OLD_KEY", reason="first")
    mark_deprecated(vault_path, "OLD_KEY", reason="second")
    data = load_deprecated(vault_path)
    assert data["OLD_KEY"]["reason"] == "second"


def test_unmark_removes_entry(vault_path):
    mark_deprecated(vault_path, "OLD_KEY")
    result = unmark_deprecated(vault_path, "OLD_KEY")
    assert result is True
    assert not is_deprecated(vault_path, "OLD_KEY")


def test_unmark_missing_key_returns_false(vault_path):
    result = unmark_deprecated(vault_path, "NONEXISTENT")
    assert result is False


def test_is_deprecated_true(vault_path):
    mark_deprecated(vault_path, "LEGACY")
    assert is_deprecated(vault_path, "LEGACY") is True


def test_is_deprecated_false(vault_path):
    assert is_deprecated(vault_path, "ACTIVE_KEY") is False


def test_deprecation_warning_none_for_active_key(vault_path):
    assert deprecation_warning(vault_path, "ACTIVE") is None


def test_deprecation_warning_contains_key(vault_path):
    mark_deprecated(vault_path, "OLD")
    msg = deprecation_warning(vault_path, "OLD")
    assert "OLD" in msg


def test_deprecation_warning_includes_reason(vault_path):
    mark_deprecated(vault_path, "X", reason="no longer needed")
    msg = deprecation_warning(vault_path, "X")
    assert "no longer needed" in msg


def test_deprecation_warning_includes_replacement(vault_path):
    mark_deprecated(vault_path, "X", replacement="NEW_X")
    msg = deprecation_warning(vault_path, "X")
    assert "NEW_X" in msg
