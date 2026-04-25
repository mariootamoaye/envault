"""Tests for envault.cli_reorder."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_reorder import cmd_reorder


@pytest.fixture()
def runner():
    return CliRunner()


def _make_store(tmp_path: Path, data: dict[str, str]):
    """Create a minimal VaultStore-like object backed by tmp_path."""
    from envault.store import VaultStore

    store = VaultStore.__new__(VaultStore)
    store._path = tmp_path / "vault.json"
    store._data = dict(data)

    def _save():
        import json
        store._path.write_text(json.dumps(store._data))

    store.save = _save
    store.keys = lambda: list(store._data.keys())
    store.get = lambda k: store._data[k]
    store.set = lambda k, v: store._data.__setitem__(k, v)
    store.unset = lambda k: store._data.pop(k, None)
    return store


def _invoke(runner, tmp_path, data, args):
    store = _make_store(tmp_path, data)
    with (
        patch("envault.cli_reorder._prompt_password", return_value="pw"),
        patch("envault.cli_reorder._get_store", return_value=store),
    ):
        result = runner.invoke(cmd_reorder, args, catch_exceptions=False)
    return result, store


def test_sort_alpha(runner, tmp_path):
    result, store = _invoke(
        runner, tmp_path, {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}, ["sort"]
    )
    assert result.exit_code == 0
    assert "Sorted 3 key(s)" in result.output
    assert store.keys() == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_alpha_desc(runner, tmp_path):
    result, store = _invoke(
        runner, tmp_path, {"ZEBRA": "1", "APPLE": "2"}, ["sort", "--mode", "alpha_desc"]
    )
    assert result.exit_code == 0
    assert store.keys() == ["ZEBRA", "APPLE"]


def test_sort_invalid_mode(runner, tmp_path):
    store = _make_store(tmp_path, {"A": "1"})
    with (
        patch("envault.cli_reorder._prompt_password", return_value="pw"),
        patch("envault.cli_reorder._get_store", return_value=store),
    ):
        result = runner.invoke(cmd_reorder, ["sort", "--mode", "bogus"])
    assert result.exit_code != 0


def test_move_key_success(runner, tmp_path):
    result, store = _invoke(
        runner, tmp_path, {"A": "1", "B": "2", "C": "3"}, ["move", "C", "0"]
    )
    assert result.exit_code == 0
    assert "Moved 'C' to position 0" in result.output
    assert store.keys()[0] == "C"


def test_move_key_missing_key(runner, tmp_path):
    result, _store = _invoke(
        runner, tmp_path, {"A": "1"}, ["move", "MISSING", "0"]
    )
    assert result.exit_code != 0
    assert "not found" in result.output
