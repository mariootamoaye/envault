"""Tests for envault.quota module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.quota import (
    DEFAULT_QUOTA,
    QuotaExceededError,
    check_quota,
    get_quota,
    load_quota,
    remove_quota,
    set_quota,
)


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vault"


def test_load_returns_empty_when_no_file(vault_dir):
    assert load_quota(vault_dir) == {}


def test_get_quota_returns_default_when_unset(vault_dir):
    assert get_quota(vault_dir) == DEFAULT_QUOTA


def test_set_quota_persists_limit(vault_dir):
    set_quota(vault_dir, 100)
    assert get_quota(vault_dir) == 100


def test_set_quota_creates_directory(tmp_path):
    nested = tmp_path / "a" / "b" / "vault"
    set_quota(nested, 50)
    assert get_quota(nested) == 50


def test_set_quota_rejects_zero(vault_dir):
    with pytest.raises(ValueError, match=">= 1"):
        set_quota(vault_dir, 0)


def test_set_quota_rejects_negative(vault_dir):
    with pytest.raises(ValueError, match=">= 1"):
        set_quota(vault_dir, -10)


def test_set_quota_overwrites_existing(vault_dir):
    set_quota(vault_dir, 100)
    set_quota(vault_dir, 250)
    assert get_quota(vault_dir) == 250


def test_remove_quota_reverts_to_default(vault_dir):
    set_quota(vault_dir, 42)
    remove_quota(vault_dir)
    assert get_quota(vault_dir) == DEFAULT_QUOTA


def test_remove_quota_no_file_is_safe(vault_dir):
    # Should not raise even if no quota file exists
    remove_quota(vault_dir)


def test_check_quota_passes_under_limit(vault_dir):
    set_quota(vault_dir, 10)
    # Should not raise
    check_quota(vault_dir, current_count=5, adding=4)


def test_check_quota_passes_at_exact_limit(vault_dir):
    set_quota(vault_dir, 10)
    check_quota(vault_dir, current_count=9, adding=1)


def test_check_quota_raises_when_exceeded(vault_dir):
    set_quota(vault_dir, 10)
    with pytest.raises(QuotaExceededError, match="Quota exceeded"):
        check_quota(vault_dir, current_count=10, adding=1)


def test_check_quota_default_limit_used_when_unset(vault_dir):
    # With default quota, adding 1 to 0 should be fine
    check_quota(vault_dir, current_count=0, adding=1)


def test_quota_exceeded_error_message_contains_details(vault_dir):
    set_quota(vault_dir, 5)
    with pytest.raises(QuotaExceededError) as exc_info:
        check_quota(vault_dir, current_count=5, adding=2)
    msg = str(exc_info.value)
    assert "5" in msg
    assert "2" in msg
