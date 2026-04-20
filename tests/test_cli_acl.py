"""Tests for envault.cli_acl."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.acl import load_acl, set_permission
from envault.cli_acl import cmd_acl


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    """Patch vault_path_for_profile to point inside tmp_path."""
    vault_file = tmp_path / ".envault" / "default.vault"
    vault_file.parent.mkdir(parents=True, exist_ok=True)

    import envault.cli_acl as cli_acl_mod

    monkeypatch.setattr(
        cli_acl_mod,
        "vault_path_for_profile",
        lambda _profile: vault_file,
    )
    return vault_file.parent


def _invoke(runner, vault_dir, *args):
    return runner.invoke(cmd_acl, list(args))


def test_grant_creates_permission(runner, vault_dir):
    result = _invoke(runner, vault_dir, "grant", "dev", "read", "DB_URL", "API_KEY")
    assert result.exit_code == 0
    assert "Granted" in result.output
    acl = load_acl(vault_dir)
    assert "DB_URL" in acl["dev"]["read"]


def test_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No ACL" in result.output


def test_list_shows_roles(runner, vault_dir):
    set_permission(vault_dir, "ops", "write", ["SECRET"])
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "ops" in result.output
    assert "SECRET" in result.output


def test_revoke_removes_role(runner, vault_dir):
    set_permission(vault_dir, "ci", "read", ["TOKEN"])
    result = _invoke(runner, vault_dir, "revoke", "ci")
    assert result.exit_code == 0
    assert "ci" not in load_acl(vault_dir)


def test_check_allow(runner, vault_dir):
    set_permission(vault_dir, "admin", "read", ["KEY"])
    result = _invoke(runner, vault_dir, "check", "admin", "read", "KEY")
    assert result.exit_code == 0
    assert "ALLOW" in result.output


def test_check_deny(runner, vault_dir):
    result = _invoke(runner, vault_dir, "check", "stranger", "read", "KEY")
    assert result.exit_code != 0
    assert "DENY" in result.output
