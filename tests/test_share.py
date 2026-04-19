"""Tests for envault.share module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.share import export_bundle, import_bundle, save_bundle_file, load_bundle_file


SECRETS = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/db"}
PASSWORD = "hunter2"


def test_export_bundle_returns_string():
    bundle = export_bundle(SECRETS, PASSWORD)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_import_bundle_roundtrip():
    bundle = export_bundle(SECRETS, PASSWORD)
    result = import_bundle(bundle, PASSWORD)
    assert result == SECRETS


def test_import_bundle_wrong_password_raises():
    bundle = export_bundle(SECRETS, PASSWORD)
    with pytest.raises(Exception):
        import_bundle(bundle, "wrongpassword")


def test_import_bundle_invalid_format_raises():
    with pytest.raises(ValueError, match="Invalid bundle format"):
        import_bundle("!!!not-valid-base64!!!", PASSWORD)


def test_export_different_passwords_produce_different_bundles():
    b1 = export_bundle(SECRETS, "pass1")
    b2 = export_bundle(SECRETS, "pass2")
    assert b1 != b2


def test_save_and_load_bundle_file(tmp_path: Path):
    bundle = export_bundle(SECRETS, PASSWORD)
    bundle_file = tmp_path / "vault.bundle"
    save_bundle_file(bundle, bundle_file)
    loaded = load_bundle_file(bundle_file)
    assert loaded == bundle


def test_load_bundle_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_bundle_file(tmp_path / "nonexistent.bundle")


def test_empty_secrets_roundtrip():
    bundle = export_bundle({}, PASSWORD)
    result = import_bundle(bundle, PASSWORD)
    assert result == {}
