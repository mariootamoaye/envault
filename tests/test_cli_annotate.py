"""Tests for envault.cli_annotate."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_annotate import cmd_annotate


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, vault_path, *args):
    return runner.invoke(cmd_annotate, [*args, "--vault", str(vault_path)])


def test_set_creates_annotation(runner, tmp_path):
    vp = tmp_path / "vault.json"
    result = _invoke(runner, vp, "set", "DB_URL", "primary db")
    assert result.exit_code == 0
    assert "Annotation set" in result.output


def test_get_returns_note(runner, tmp_path):
    vp = tmp_path / "vault.json"
    _invoke(runner, vp, "set", "API_KEY", "rotate monthly")
    result = _invoke(runner, vp, "get", "API_KEY")
    assert result.exit_code == 0
    assert "rotate monthly" in result.output


def test_get_missing_key(runner, tmp_path):
    vp = tmp_path / "vault.json"
    result = _invoke(runner, vp, "get", "MISSING")
    assert result.exit_code == 0
    assert "No annotation" in result.output


def test_remove_existing(runner, tmp_path):
    vp = tmp_path / "vault.json"
    _invoke(runner, vp, "set", "FOO", "bar")
    result = _invoke(runner, vp, "remove", "FOO")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing(runner, tmp_path):
    vp = tmp_path / "vault.json"
    result = _invoke(runner, vp, "remove", "GHOST")
    assert result.exit_code == 0
    assert "No annotation found" in result.output


def test_list_shows_all(runner, tmp_path):
    vp = tmp_path / "vault.json"
    _invoke(runner, vp, "set", "A", "note a")
    _invoke(runner, vp, "set", "B", "note b")
    result = _invoke(runner, vp, "list")
    assert result.exit_code == 0
    assert "A: note a" in result.output
    assert "B: note b" in result.output


def test_list_empty_vault(runner, tmp_path):
    vp = tmp_path / "vault.json"
    result = _invoke(runner, vp, "list")
    assert result.exit_code == 0
    assert "No annotations" in result.output
