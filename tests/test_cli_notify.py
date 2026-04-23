"""Tests for the notify CLI sub-commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_notify import cmd_notify
from envault.notify import add_notify


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def _invoke(runner: CliRunner, vault_path: Path, *args: str):
    return runner.invoke(
        cmd_notify,
        list(args),
        obj={"vault_path": vault_path},
        catch_exceptions=False,
    )


def test_add_success(runner: CliRunner, vault_path: Path) -> None:
    result = _invoke(runner, vault_path, "add", "set", "echo hello")
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_add_unknown_event_shows_error(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        cmd_notify,
        ["add", "bad_event", "cmd"],
        obj={"vault_path": vault_path},
    )
    assert result.exit_code != 0
    assert "Unknown event" in result.output


def test_remove_existing(runner: CliRunner, vault_path: Path) -> None:
    add_notify(vault_path, "unset", "echo bye")
    result = _invoke(runner, vault_path, "remove", "unset", "echo bye")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing(runner: CliRunner, vault_path: Path) -> None:
    result = _invoke(runner, vault_path, "remove", "set", "ghost")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_list_empty(runner: CliRunner, vault_path: Path) -> None:
    result = _invoke(runner, vault_path, "list")
    assert result.exit_code == 0
    assert "No notifications" in result.output


def test_list_shows_entries(runner: CliRunner, vault_path: Path) -> None:
    add_notify(vault_path, "rotate", "slack_notify.sh")
    add_notify(vault_path, "import", "log_import.sh")
    result = _invoke(runner, vault_path, "list")
    assert result.exit_code == 0
    assert "rotate: slack_notify.sh" in result.output
    assert "import: log_import.sh" in result.output


def test_fire_no_commands(runner: CliRunner, vault_path: Path) -> None:
    result = _invoke(runner, vault_path, "fire", "expire")
    assert result.exit_code == 0
    assert "No commands registered" in result.output


def test_fire_runs_command(runner: CliRunner, vault_path: Path) -> None:
    add_notify(vault_path, "set", "true")
    result = _invoke(runner, vault_path, "fire", "set")
    assert result.exit_code == 0
    assert "ok" in result.output
