"""Tests for envault.cli_backup CLI commands."""

import gzip
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_backup import cmd_backup


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_and_dirs(tmp_path):
    vault = tmp_path / "vault.json"
    vault.write_text(json.dumps({"KEY": "val"}))
    bdir = tmp_path / "backups"
    return vault, bdir


def _invoke(runner, args, **kwargs):
    return runner.invoke(cmd_backup, args, catch_exceptions=False, **kwargs)


def test_backup_create_success(runner, vault_and_dirs, monkeypatch):
    vault, bdir = vault_and_dirs
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: vault)
    result = _invoke(runner, ["create", "--backup-dir", str(bdir)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_missing_vault(runner, tmp_path, monkeypatch):
    missing = tmp_path / "no_vault.json"
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: missing)
    result = runner.invoke(
        cmd_backup, ["create", "--backup-dir", str(tmp_path / "bk")]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_backup_list_shows_backups(runner, vault_and_dirs, monkeypatch):
    vault, bdir = vault_and_dirs
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: vault)
    _invoke(runner, ["create", "--backup-dir", str(bdir)])
    result = _invoke(runner, ["list", "--backup-dir", str(bdir)])
    assert result.exit_code == 0
    assert ".gz" in result.output


def test_backup_list_empty(runner, tmp_path, monkeypatch):
    vault = tmp_path / "vault.json"
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: vault)
    bdir = tmp_path / "empty_bk"
    result = _invoke(runner, ["list", "--backup-dir", str(bdir)])
    assert "No backups found" in result.output


def test_backup_restore_success(runner, vault_and_dirs, monkeypatch):
    vault, bdir = vault_and_dirs
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: vault)
    _invoke(runner, ["create", "--backup-dir", str(bdir)])
    backup_file = list(bdir.glob("*.gz"))[0]
    result = runner.invoke(
        cmd_backup,
        ["restore", str(backup_file)],
        input="y\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "restored" in result.output


def test_backup_delete_success(runner, vault_and_dirs, monkeypatch):
    vault, bdir = vault_and_dirs
    monkeypatch.setattr("envault.cli_backup.vault_path_for_profile", lambda _: vault)
    _invoke(runner, ["create", "--backup-dir", str(bdir)])
    backup_file = list(bdir.glob("*.gz"))[0]
    result = _invoke(runner, ["delete", str(backup_file)])
    assert result.exit_code == 0
    assert "Deleted" in result.output
    assert not backup_file.exists()
