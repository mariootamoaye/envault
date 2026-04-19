"""Tests for the rotate CLI command."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.store import VaultStore


@pytest.fixture()
def runner():
    return CliRunner()


def _make_store(tmp_path, password="old-pass"):
    path = tmp_path / "vault.json"
    store = VaultStore(path, password)
    store.load()
    store.set("FOO", "bar")
    store.save()
    return path


def test_rotate_success(runner, tmp_path, monkeypatch):
    vault_path = _make_store(tmp_path)
    monkeypatch.setenv("ENVAULT_VAULT_PATH", str(vault_path))

    result = runner.invoke(
        cli,
        ["rotate"],
        input="old-pass\nnew-pass\nnew-pass\n",
    )
    assert result.exit_code == 0
    assert "Rotated 1 secret" in result.output


def test_rotate_wrong_current_password(runner, tmp_path, monkeypatch):
    vault_path = _make_store(tmp_path)
    monkeypatch.setenv("ENVAULT_VAULT_PATH", str(vault_path))

    result = runner.invoke(
        cli,
        ["rotate"],
        input="wrong\nnew-pass\nnew-pass\n",
    )
    assert result.exit_code != 0
    assert "incorrect" in result.output.lower() or "Error" in result.output


def test_rotate_same_password_rejected(runner, tmp_path, monkeypatch):
    vault_path = _make_store(tmp_path)
    monkeypatch.setenv("ENVAULT_VAULT_PATH", str(vault_path))

    result = runner.invoke(
        cli,
        ["rotate"],
        input="old-pass\nold-pass\nold-pass\n",
    )
    assert result.exit_code != 0
    assert "differ" in result.output.lower() or "Error" in result.output
