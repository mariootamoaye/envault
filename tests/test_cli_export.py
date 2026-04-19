"""Tests for the export CLI command."""
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import pytest

from envault.cli_export import cmd_export


@pytest.fixture()
def runner():
    return CliRunner()


def _make_store(data: dict):
    store = MagicMock()
    store.all.return_value = data
    return store


@patch("envault.cli_export._prompt_password", return_value="pass")
@patch("envault.cli_export._get_store")
def test_export_dotenv(mock_store, mock_pw, runner):
    mock_store.return_value = _make_store({"KEY": "val"})
    result = runner.invoke(cmd_export, ["--format", "dotenv"])
    assert result.exit_code == 0
    assert "KEY=" in result.output


@patch("envault.cli_export._prompt_password", return_value="pass")
@patch("envault.cli_export._get_store")
def test_export_bash(mock_store, mock_pw, runner):
    mock_store.return_value = _make_store({"FOO": "bar"})
    result = runner.invoke(cmd_export, ["--format", "bash"])
    assert result.exit_code == 0
    assert "export FOO=" in result.output


@patch("envault.cli_export._prompt_password", return_value="pass")
@patch("envault.cli_export._get_store")
def test_export_fish(mock_store, mock_pw, runner):
    mock_store.return_value = _make_store({"FOO": "bar"})
    result = runner.invoke(cmd_export, ["--format", "fish"])
    assert result.exit_code == 0
    assert "set -x FOO" in result.output


@patch("envault.cli_export._prompt_password", return_value="pass")
@patch("envault.cli_export._get_store")
def test_export_empty_vault(mock_store, mock_pw, runner):
    mock_store.return_value = _make_store({})
    result = runner.invoke(cmd_export, [])
    assert result.exit_code == 0
    assert "empty" in result.output.lower()


@patch("envault.cli_export._prompt_password", return_value="pass")
@patch("envault.cli_export._get_store")
def test_export_to_file(mock_store, mock_pw, runner, tmp_path):
    mock_store.return_value = _make_store({"SECRET": "xyz"})
    out_file = tmp_path / "env.txt"
    result = runner.invoke(cmd_export, ["--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "SECRET=" in content
