"""Tests for envault.signing."""

import pytest
from pathlib import Path

from envault.signing import (
    sign,
    verify,
    save_signature,
    load_signature,
    verify_vault,
    clear_signature,
)

SECRET = "supersecret"
DATA = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/dev"}


# ---------------------------------------------------------------------------
# sign / verify
# ---------------------------------------------------------------------------

def test_sign_returns_hex_string():
    sig = sign(DATA, SECRET)
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest


def test_sign_is_deterministic():
    assert sign(DATA, SECRET) == sign(DATA, SECRET)


def test_sign_order_independent():
    data_reversed = dict(reversed(list(DATA.items())))
    assert sign(DATA, SECRET) == sign(data_reversed, SECRET)


def test_sign_differs_for_different_secret():
    assert sign(DATA, SECRET) != sign(DATA, "other")


def test_sign_differs_for_different_data():
    other = {**DATA, "EXTRA": "value"}
    assert sign(DATA, SECRET) != sign(other, SECRET)


def test_verify_correct_signature():
    sig = sign(DATA, SECRET)
    assert verify(DATA, SECRET, sig) is True


def test_verify_wrong_secret():
    sig = sign(DATA, SECRET)
    assert verify(DATA, "wrong", sig) is False


def test_verify_tampered_data():
    sig = sign(DATA, SECRET)
    tampered = {**DATA, "API_KEY": "hacked"}
    assert verify(tampered, SECRET, sig) is False


# ---------------------------------------------------------------------------
# save / load / verify_vault / clear
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.json"


def test_save_and_load_signature(vault_path):
    save_signature(vault_path, DATA, SECRET)
    loaded = load_signature(vault_path)
    assert loaded == sign(DATA, SECRET)


def test_load_signature_missing_returns_none(vault_path):
    assert load_signature(vault_path) is None


def test_verify_vault_success(vault_path):
    save_signature(vault_path, DATA, SECRET)
    assert verify_vault(vault_path, DATA, SECRET) is True


def test_verify_vault_no_sig_file(vault_path):
    assert verify_vault(vault_path, DATA, SECRET) is False


def test_verify_vault_wrong_secret(vault_path):
    save_signature(vault_path, DATA, SECRET)
    assert verify_vault(vault_path, DATA, "wrong") is False


def test_clear_signature_removes_file(vault_path):
    save_signature(vault_path, DATA, SECRET)
    clear_signature(vault_path)
    assert load_signature(vault_path) is None


def test_clear_signature_no_file_is_noop(vault_path):
    clear_signature(vault_path)  # should not raise
