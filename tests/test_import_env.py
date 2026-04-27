"""Tests for envault.import_env."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from envault.import_env import parse_dotenv, import_from_file, import_from_env


def test_parse_dotenv_simple():
    text = "FOO=bar\nBAZ=qux\n"
    result = parse_dotenv(text)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_ignores_comments():
    text = "# comment\nKEY=value\n"
    assert parse_dotenv(text) == {"KEY": "value"}


def test_parse_dotenv_strips_double_quotes():
    assert parse_dotenv('KEY="hello world"') == {"KEY": "hello world"}


def test_parse_dotenv_strips_single_quotes():
    assert parse_dotenv("KEY='hello world'") == {"KEY": "hello world"}


def test_parse_dotenv_export_prefix():
    assert parse_dotenv("export MY_VAR=123") == {"MY_VAR": "123"}


def test_parse_dotenv_empty_value():
    assert parse_dotenv("EMPTY=") == {"EMPTY": ""}


def test_parse_dotenv_ignores_blank_lines():
    text = "\n\nA=1\n\nB=2\n"
    assert parse_dotenv(text) == {"A": "1", "B": "2"}


def test_import_from_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("HOST=localhost\nPORT=5432\n")
    result = import_from_file(env_file)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_import_from_file_missing_raises(tmp_path: Path):
    """import_from_file should raise FileNotFoundError for a non-existent path."""
    missing = tmp_path / "does_not_exist.env"
    with pytest.raises(FileNotFoundError):
        import_from_file(missing)


def test_import_from_env_all(monkeypatch):
    monkeypatch.setenv("_TEST_VAR", "hello")
    result = import_from_env()
    assert "_TEST_VAR" in result
    assert result["_TEST_VAR"] == "hello"


def test_import_from_env_filtered(monkeypatch):
    monkeypatch.setenv("_A", "1")
    monkeypatch.setenv("_B", "2")
    result = import_from_env(keys=["_A"])
    assert "_A" in result
    assert "_B" not in result
