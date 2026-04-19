"""Tests for envault.profile."""
from pathlib import Path

import pytest

from envault.profile import (
    DEFAULT_PROFILE,
    get_profile_name,
    list_profiles,
    vault_path_for_profile,
)


def test_get_profile_name_default():
    assert get_profile_name() == DEFAULT_PROFILE


def test_get_profile_name_override():
    assert get_profile_name(override="staging") == "staging"


def test_get_profile_name_from_env(monkeypatch):
    monkeypatch.setenv("ENVAULT_PROFILE", "prod")
    assert get_profile_name() == "prod"


def test_get_profile_name_override_beats_env(monkeypatch):
    monkeypatch.setenv("ENVAULT_PROFILE", "prod")
    assert get_profile_name(override="dev") == "dev"


def test_vault_path_default(tmp_path):
    p = vault_path_for_profile(tmp_path, DEFAULT_PROFILE)
    assert p == tmp_path / "vault.enc"


def test_vault_path_named(tmp_path):
    p = vault_path_for_profile(tmp_path, "staging")
    assert p == tmp_path / "vault.staging.enc"


def test_vault_path_creates_dir(tmp_path):
    new_dir = tmp_path / "nested" / "dir"
    vault_path_for_profile(new_dir, DEFAULT_PROFILE)
    assert new_dir.exists()


def test_list_profiles_empty(tmp_path):
    assert list_profiles(tmp_path) == []


def test_list_profiles_missing_dir(tmp_path):
    assert list_profiles(tmp_path / "nonexistent") == []


def test_list_profiles_finds_profiles(tmp_path):
    (tmp_path / "vault.enc").touch()
    (tmp_path / "vault.dev.enc").touch()
    (tmp_path / "vault.prod.enc").touch()
    profiles = list_profiles(tmp_path)
    assert DEFAULT_PROFILE in profiles
    assert "dev" in profiles
    assert "prod" in profiles
    assert len(profiles) == 3
