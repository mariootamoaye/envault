"""Tests for envault.redact."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.redact import (
    add_pattern,
    is_redacted,
    load_redact,
    pin_key,
    redact_dict,
    unpin_key,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.enc"


# ── load / defaults ──────────────────────────────────────────────────────────

def test_load_returns_defaults_when_no_file(vault_path):
    cfg = load_redact(vault_path)
    assert "patterns" in cfg
    assert "keys" in cfg
    assert isinstance(cfg["patterns"], list)
    assert len(cfg["patterns"]) > 0


# ── default pattern matching ─────────────────────────────────────────────────

@pytest.mark.parametrize("key", ["PASSWORD", "api_key", "SECRET_TOKEN", "DB_PASSWORD", "private_key"])
def test_default_patterns_match_sensitive_keys(vault_path, key):
    assert is_redacted(vault_path, key)


def test_default_patterns_do_not_match_plain_key(vault_path):
    assert not is_redacted(vault_path, "DATABASE_HOST")
    assert not is_redacted(vault_path, "APP_ENV")


# ── explicit pin / unpin ─────────────────────────────────────────────────────

def test_pin_key_marks_as_redacted(vault_path):
    pin_key(vault_path, "MY_CUSTOM_VAR")
    assert is_redacted(vault_path, "MY_CUSTOM_VAR")


def test_pin_key_idempotent(vault_path):
    pin_key(vault_path, "MY_CUSTOM_VAR")
    pin_key(vault_path, "MY_CUSTOM_VAR")
    cfg = load_redact(vault_path)
    assert cfg["keys"].count("MY_CUSTOM_VAR") == 1


def test_unpin_key_removes_mark(vault_path):
    pin_key(vault_path, "MY_CUSTOM_VAR")
    unpin_key(vault_path, "MY_CUSTOM_VAR")
    assert not is_redacted(vault_path, "MY_CUSTOM_VAR")


def test_unpin_nonexistent_key_is_safe(vault_path):
    unpin_key(vault_path, "DOES_NOT_EXIST")  # should not raise


# ── custom patterns ──────────────────────────────────────────────────────────

def test_add_pattern_matches_new_key(vault_path):
    add_pattern(vault_path, r"(?i)internal")
    assert is_redacted(vault_path, "INTERNAL_FLAG")


def test_add_invalid_pattern_raises(vault_path):
    with pytest.raises(re.error if False else Exception):
        add_pattern(vault_path, "[invalid")


def test_add_pattern_idempotent(vault_path):
    add_pattern(vault_path, r"(?i)custom")
    add_pattern(vault_path, r"(?i)custom")
    cfg = load_redact(vault_path)
    assert cfg["patterns"].count(r"(?i)custom") == 1


# ── redact_dict ───────────────────────────────────────────────────────────────

def test_redact_dict_replaces_sensitive_values(vault_path):
    data = {"API_KEY": "abc123", "HOST": "localhost"}
    result = redact_dict(vault_path, data)
    assert result["API_KEY"] == "**REDACTED**"
    assert result["HOST"] == "localhost"


def test_redact_dict_custom_placeholder(vault_path):
    pin_key(vault_path, "X")
    result = redact_dict(vault_path, {"X": "val"}, placeholder="***")
    assert result["X"] == "***"


def test_redact_dict_does_not_mutate_original(vault_path):
    original = {"API_KEY": "secret"}
    redact_dict(vault_path, original)
    assert original["API_KEY"] == "secret"


import re  # noqa: E402  (needed for parametrize reference above)
