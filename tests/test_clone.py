"""Tests for envault.clone and the CLI wrapper."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.store import VaultStore
from envault.clone import clone_vault
from envault.cli_clone import cmd_clone


PASSWORD = "test-secret"


@pytest.fixture()
def src_store(tmp_path):
    store = VaultStore(tmp_path / "src.json", PASSWORD)
    store.load()
    store.set("DB_HOST", "localhost")
    store.set("DB_PORT", "5432")
    store.set("API_KEY", "abc123")
    store.save()
    return store


def test_clone_copies_all_keys(src_store, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "envault.clone.vault_path_for_profile",
        lambda name: tmp_path / f"{name}.json",
    )
    report = clone_vault(src_store, "staging", PASSWORD)
    assert report["DB_HOST"] == "copied"
    assert report["DB_PORT"] == "copied"
    assert report["API_KEY"] == "copied"


def test_clone_respects_key_filter(src_store, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "envault.clone.vault_path_for_profile",
        lambda name: tmp_path / f"{name}.json",
    )
    report = clone_vault(src_store, "staging", PASSWORD, keys=["DB_HOST"])
    assert report["DB_HOST"] == "copied"
    assert "DB_PORT" not in report


def test_clone_skips_existing_without_overwrite(src_store, tmp_path, monkeypatch):
    dest_path = tmp_path / "dest.json"
    monkeypatch.setattr(
        "envault.clone.vault_path_for_profile",
        lambda name: dest_path,
    )
    # Pre-populate dest with DB_HOST
    dest = VaultStore(dest_path, PASSWORD)
    dest.load()
    dest.set("DB_HOST", "existing")
    dest.save()

    report = clone_vault(src_store, "dest", PASSWORD, overwrite=False)
    assert report["DB_HOST"] == "skipped"
    assert report["DB_PORT"] == "copied"


def test_clone_overwrites_when_flag_set(src_store, tmp_path, monkeypatch):
    dest_path = tmp_path / "dest.json"
    monkeypatch.setattr(
        "envault.clone.vault_path_for_profile",
        lambda name: dest_path,
    )
    dest = VaultStore(dest_path, PASSWORD)
    dest.load()
    dest.set("DB_HOST", "old")
    dest.save()

    report = clone_vault(src_store, "dest", PASSWORD, overwrite=True)
    assert report["DB_HOST"] == "copied"


def test_clone_missing_key_reported(src_store, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "envault.clone.vault_path_for_profile",
        lambda name: tmp_path / f"{name}.json",
    )
    report = clone_vault(src_store, "staging", PASSWORD, keys=["NONEXISTENT"])
    assert report["NONEXISTENT"] == "missing"


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_clone_same_profile_error(runner):
    result = runner.invoke(cmd_clone, ["run", "default", "--profile", "default"])
    assert result.exit_code != 0
    assert "differ" in result.output.lower() or result.exception
