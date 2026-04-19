"""Integration tests for the envault CLI."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.store import VaultStore

PASSWORD = "s3cr3t"


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_PATH", str(tmp_path / ".envault"))
    return CliRunner()


def test_set_stores_variable(runner):
    result = runner.invoke(cli, ["set", "API_KEY", "abc123"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_list_shows_stored_keys(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_PATH", str(tmp_path / ".envault"))
    store = VaultStore(path=tmp_path / ".envault")
    store.save({"FOO": "1", "BAR": "2"}, PASSWORD)

    result = runner.invoke(cli, ["list"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "BAR" in result.output
    assert "FOO" in result.output


def test_list_empty_vault(runner):
    result = runner.invoke(cli, ["list"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "empty" in result.output


def test_unset_existing_key(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_PATH", str(tmp_path / ".envault"))
    store = VaultStore(path=tmp_path / ".envault")
    store.set("REMOVE_ME", "val", PASSWORD)

    result = runner.invoke(cli, ["unset", "REMOVE_ME"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_unset_missing_key_warns(runner):
    result = runner.invoke(cli, ["unset", "GHOST"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_export_outputs_export_statements(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_PATH", str(tmp_path / ".envault"))
    store = VaultStore(path=tmp_path / ".envault")
    store.save({"MY_VAR": "hello"}, PASSWORD)

    result = runner.invoke(cli, ["export"], input=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "export MY_VAR=" in result.output
