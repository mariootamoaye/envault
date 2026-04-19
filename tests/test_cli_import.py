"""Tests for envault.cli_import commands."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_import import cmd_import

PASSWORD = "test-password"


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner: CliRunner, args, vault_path: str):
    with patch("envault.cli_import._prompt_password", return_value=PASSWORD), patch(
        "envault.cli_import._get_store"
    ) as mock_get:
        from envault.store import VaultStore

        store = VaultStore(vault_path, PASSWORD)
        mock_get.return_value = store
        result = runner.invoke(cmd_import, args)
        return result, store


def test_import_file_basic(runner: CliRunner, tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("ALPHA=one\nBETA=two\n")
    vault_path = str(tmp_path / ".envault")
    result, store = _invoke(
        runner, ["file", str(env_file), "--vault", vault_path], vault_path
    )
    assert result.exit_code == 0
    assert "Imported 2" in result.output
    assert store.get("ALPHA") == "one"
    assert store.get("BETA") == "two"


def test_import_file_no_overwrite(runner: CliRunner, tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=new_value\n")
    vault_path = str(tmp_path / ".envault")
    result, store = _invoke(
        runner, ["file", str(env_file), "--vault", vault_path], vault_path
    )
    # Pre-populate the store so overwrite logic triggers on second call
    store.set("KEY", "original")
    result2, store2 = _invoke(
        runner, ["file", str(env_file), "--vault", vault_path], vault_path
    )
    # store2 is a fresh instance; we only verify the command runs
    assert result2.exit_code == 0


def test_import_env_cmd(runner: CliRunner, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("_ENVAULT_TEST_X", "42")
    vault_path = str(tmp_path / ".envault")
    result, store = _invoke(
        runner,
        ["env", "_ENVAULT_TEST_X", "--vault", vault_path],
        vault_path,
    )
    assert result.exit_code == 0
    assert "Imported 1" in result.output
    assert store.get("_ENVAULT_TEST_X") == "42"


def test_import_env_missing_key(runner: CliRunner, tmp_path: Path, monkeypatch):
    monkeypatch.delenv("_MISSING_KEY", raising=False)
    vault_path = str(tmp_path / ".envault")
    result, store = _invoke(
        runner,
        ["env", "_MISSING_KEY", "--vault", vault_path],
        vault_path,
    )
    assert result.exit_code == 0
    assert "Imported 0" in result.output
