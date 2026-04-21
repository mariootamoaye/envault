"""Tests for envault.checksum."""

import pytest
from pathlib import Path

from envault.checksum import (
    compute_checksum,
    save_checksum,
    load_checksum,
    verify,
    update,
    delete_checksum,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_compute_checksum_returns_hex_string():
    result = compute_checksum({"FOO": "bar"})
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex digest length


def test_compute_checksum_is_deterministic():
    data = {"A": "1", "B": "2"}
    assert compute_checksum(data) == compute_checksum(data)


def test_compute_checksum_order_independent():
    a = compute_checksum({"X": "1", "Y": "2"})
    b = compute_checksum({"Y": "2", "X": "1"})
    assert a == b


def test_compute_checksum_differs_for_different_data():
    assert compute_checksum({"A": "1"}) != compute_checksum({"A": "2"})


def test_load_checksum_returns_none_when_no_file(vault_path: Path):
    assert load_checksum(vault_path) is None


def test_save_and_load_roundtrip(vault_path: Path):
    checksum = "abc123"
    save_checksum(vault_path, checksum)
    assert load_checksum(vault_path) == checksum


def test_verify_returns_false_when_no_checksum_file(vault_path: Path):
    assert verify(vault_path, {"K": "V"}) is False


def test_verify_returns_true_for_matching_data(vault_path: Path):
    data = {"SECRET": "hunter2"}
    update(vault_path, data)
    assert verify(vault_path, data) is True


def test_verify_returns_false_after_data_changed(vault_path: Path):
    data = {"SECRET": "hunter2"}
    update(vault_path, data)
    tampered = {"SECRET": "hacked"}
    assert verify(vault_path, tampered) is False


def test_update_returns_checksum_string(vault_path: Path):
    result = update(vault_path, {"FOO": "bar"})
    assert isinstance(result, str) and len(result) == 64


def test_update_persists_checksum(vault_path: Path):
    data = {"ENV": "prod"}
    checksum = update(vault_path, data)
    assert load_checksum(vault_path) == checksum


def test_delete_checksum_removes_file(vault_path: Path):
    update(vault_path, {"K": "V"})
    delete_checksum(vault_path)
    assert load_checksum(vault_path) is None


def test_delete_checksum_noop_when_no_file(vault_path: Path):
    # Should not raise even if file is absent
    delete_checksum(vault_path)
