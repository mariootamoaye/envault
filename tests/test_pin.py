"""Tests for envault.pin."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.pin import (
    load_pins,
    save_pins,
    pin_key,
    unpin_key,
    is_pinned,
    assert_not_pinned,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vault"


def test_load_returns_empty_when_no_file(vault_dir):
    assert load_pins(vault_dir) == []


def test_pin_key_creates_file(vault_dir):
    pin_key(vault_dir, "API_KEY")
    assert (vault_dir / ".pins.json").exists()


def test_pin_key_is_persisted(vault_dir):
    pin_key(vault_dir, "API_KEY")
    assert "API_KEY" in load_pins(vault_dir)


def test_pin_key_idempotent(vault_dir):
    pin_key(vault_dir, "API_KEY")
    pin_key(vault_dir, "API_KEY")
    assert load_pins(vault_dir).count("API_KEY") == 1


def test_pin_multiple_keys(vault_dir):
    pin_key(vault_dir, "KEY_A")
    pin_key(vault_dir, "KEY_B")
    pins = load_pins(vault_dir)
    assert "KEY_A" in pins
    assert "KEY_B" in pins


def test_pins_stored_sorted(vault_dir):
    pin_key(vault_dir, "ZEBRA")
    pin_key(vault_dir, "ALPHA")
    assert load_pins(vault_dir) == ["ALPHA", "ZEBRA"]


def test_unpin_removes_key(vault_dir):
    pin_key(vault_dir, "API_KEY")
    unpin_key(vault_dir, "API_KEY")
    assert not is_pinned(vault_dir, "API_KEY")


def test_unpin_nonexistent_is_noop(vault_dir):
    unpin_key(vault_dir, "GHOST")  # should not raise


def test_is_pinned_true(vault_dir):
    pin_key(vault_dir, "SECRET")
    assert is_pinned(vault_dir, "SECRET") is True


def test_is_pinned_false(vault_dir):
    assert is_pinned(vault_dir, "NOT_PINNED") is False


def test_assert_not_pinned_raises_for_pinned_key(vault_dir):
    pin_key(vault_dir, "DB_PASS")
    with pytest.raises(RuntimeError, match="DB_PASS"):
        assert_not_pinned(vault_dir, "DB_PASS")


def test_assert_not_pinned_passes_for_unpinned_key(vault_dir):
    assert_not_pinned(vault_dir, "SAFE_KEY")  # should not raise


def test_pin_empty_key_raises(vault_dir):
    with pytest.raises(ValueError):
        pin_key(vault_dir, "")


def test_save_and_load_roundtrip(vault_dir):
    keys = ["FOO", "BAR", "BAZ"]
    save_pins(vault_dir, keys)
    assert load_pins(vault_dir) == sorted(keys)
