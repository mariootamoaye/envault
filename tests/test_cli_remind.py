"""Tests for envault.cli_remind."""
from datetime import date, timedelta
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_remind import cmd_remind
from envault.remind import save_reminders


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, args, vault_dir):
    return runner.invoke(cmd_remind, args + ["--vault-dir", str(vault_dir)])


def test_remind_set_success(runner, tmp_path):
    result = _invoke(runner, ["set", "API_KEY", "30"], tmp_path)
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    expected = (date.today() + timedelta(days=30)).isoformat()
    assert expected in result.output


def test_remind_set_invalid_days(runner, tmp_path):
    result = _invoke(runner, ["set", "API_KEY", "0"], tmp_path)
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remind_remove_existing(runner, tmp_path):
    _invoke(runner, ["set", "SECRET", "7"], tmp_path)
    result = _invoke(runner, ["remove", "SECRET"], tmp_path)
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remind_remove_missing(runner, tmp_path):
    result = _invoke(runner, ["remove", "GHOST"], tmp_path)
    assert result.exit_code == 0
    assert "No reminder" in result.output


def test_remind_list_empty(runner, tmp_path):
    result = _invoke(runner, ["list"], tmp_path)
    assert result.exit_code == 0
    assert "No reminders" in result.output


def test_remind_list_shows_entries(runner, tmp_path):
    _invoke(runner, ["set", "DB_PASS", "14"], tmp_path)
    result = _invoke(runner, ["list"], tmp_path)
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_remind_list_due_only(runner, tmp_path):
    past = date.today() - timedelta(days=2)
    future = date.today() + timedelta(days=10)
    save_reminders(tmp_path, {"OLD": past.isoformat(), "NEW": future.isoformat()})
    result = _invoke(runner, ["list", "--due"], tmp_path)
    assert result.exit_code == 0
    assert "OLD" in result.output
    assert "NEW" not in result.output
