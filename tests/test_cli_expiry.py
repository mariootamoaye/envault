"""Tests for envault.cli_expiry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_expiry import cmd_expiry
from envault.expiry import get_expiry, set_expiry


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def _invoke(runner, vault_path, *args):
    return runner.invoke(cmd_expiry, ["--vault", str(vault_path), *args])


def test_expiry_set_success(runner, vault_path):
    result = runner.invoke(
        cmd_expiry, ["set", "API_KEY", "2099-12-31", "--vault", str(vault_path)]
    )
    assert result.exit_code == 0
    assert "2099-12-31" in result.output
    exp = get_expiry(vault_path, "API_KEY")
    assert exp is not None
    assert exp.year == 2099


def test_expiry_set_invalid_date(runner, vault_path):
    result = runner.invoke(
        cmd_expiry, ["set", "K", "not-a-date", "--vault", str(vault_path)]
    )
    assert result.exit_code != 0


def test_expiry_get_shows_date(runner, vault_path):
    set_expiry(vault_path, "K", datetime(2099, 6, 15, tzinfo=timezone.utc))
    result = runner.invoke(cmd_expiry, ["get", "K", "--vault", str(vault_path)])
    assert result.exit_code == 0
    assert "2099-06-15" in result.output


def test_expiry_get_no_expiry(runner, vault_path):
    result = runner.invoke(cmd_expiry, ["get", "MISSING", "--vault", str(vault_path)])
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_expiry_remove(runner, vault_path):
    set_expiry(vault_path, "K", datetime(2099, 1, 1, tzinfo=timezone.utc))
    result = runner.invoke(cmd_expiry, ["remove", "K", "--vault", str(vault_path)])
    assert result.exit_code == 0
    assert get_expiry(vault_path, "K") is None


def test_expiry_list_expired(runner, vault_path):
    past = datetime.now(tz=timezone.utc) - timedelta(days=1)
    set_expiry(vault_path, "OLD_KEY", past)
    result = runner.invoke(cmd_expiry, ["list", "--vault", str(vault_path)])
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output


def test_expiry_list_empty(runner, vault_path):
    result = runner.invoke(cmd_expiry, ["list", "--vault", str(vault_path)])
    assert result.exit_code == 0
    assert "No expired" in result.output
