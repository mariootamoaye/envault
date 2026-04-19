"""Tests for envault.cli_profile."""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.cli_profile import cmd_profile


@pytest.fixture()
def runner():
    return CliRunner()


def _make_store(tmp_path, profile, data: dict):
    """Helper: create a real VaultStore with data."""
    from envault.store import VaultStore
    from envault.profile import vault_path_for_profile

    path = vault_path_for_profile(tmp_path, profile)
    store = VaultStore(path)
    for k, v in data.items():
        store.set(k, v)
    store.save("secret")
    return store


def test_profile_list_empty(runner, tmp_path):
    result = runner.invoke(cmd_profile, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No profiles found" in result.output


def test_profile_list_shows_profiles(runner, tmp_path):
    (tmp_path / "vault.enc").touch()
    (tmp_path / "vault.dev.enc").touch()
    result = runner.invoke(cmd_profile, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "default" in result.output
    assert "dev" in result.output


def test_profile_copy(runner, tmp_path):
    _make_store(tmp_path, "dev", {"FOO": "bar", "BAZ": "qux"})

    from envault.store import VaultStore
    from envault.profile import vault_path_for_profile

    def fake_get_store(password, profile=None):
        path = vault_path_for_profile(tmp_path, profile or "default")
        store = VaultStore(path)
        store.load(password)
        return store

    with patch("envault.cli_profile._get_store", side_effect=fake_get_store), \
         patch("envault.cli_profile._prompt_password", return_value="secret"):
        result = runner.invoke(cmd_profile, ["copy", "dev", "staging"])

    assert result.exit_code == 0
    assert "Copied 2 variable(s)" in result.output

    staging_path = vault_path_for_profile(tmp_path, "staging")
    assert staging_path.exists()
