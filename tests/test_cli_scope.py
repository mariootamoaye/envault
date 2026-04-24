"""Tests for envault.cli_scope."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_scope import cmd_scope
from envault.scope import set_scope


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def _invoke(runner, vault_path, *args):
    return runner.invoke(cmd_scope, [*args, "--vault", str(vault_path)])


def test_scope_set_success(runner, vault_path):
    result = _invoke(runner, vault_path, "set", "API_KEY", "prod")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "prod" in result.output


def test_scope_set_empty_key_shows_error(runner, vault_path):
    result = _invoke(runner, vault_path, "set", "", "prod")
    assert result.exit_code != 0


def test_scope_unset_existing(runner, vault_path):
    set_scope(vault_path, "DB_URL", "ci")
    result = _invoke(runner, vault_path, "unset", "DB_URL")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_scope_unset_missing_key(runner, vault_path):
    result = _invoke(runner, vault_path, "unset", "GHOST")
    assert result.exit_code == 0
    assert "no scope" in result.output


def test_scope_list_empty(runner, vault_path):
    result = _invoke(runner, vault_path, "list")
    assert result.exit_code == 0
    assert "No scopes" in result.output


def test_scope_list_shows_entries(runner, vault_path):
    set_scope(vault_path, "A", "prod")
    set_scope(vault_path, "B", "ci")
    result = _invoke(runner, vault_path, "list")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "prod" in result.output


def test_scope_list_filter_by_scope(runner, vault_path):
    set_scope(vault_path, "A", "prod")
    set_scope(vault_path, "B", "ci")
    result = _invoke(runner, vault_path, "list", "--scope", "prod")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output


def test_scope_list_filter_no_match(runner, vault_path):
    result = _invoke(runner, vault_path, "list", "--scope", "ghost")
    assert result.exit_code == 0
    assert "No keys" in result.output


def test_scope_names_lists_distinct(runner, vault_path):
    set_scope(vault_path, "A", "prod")
    set_scope(vault_path, "B", "prod")
    set_scope(vault_path, "C", "ci")
    result = _invoke(runner, vault_path, "scopes")
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "ci" in result.output
    assert result.output.count("prod") == 1
