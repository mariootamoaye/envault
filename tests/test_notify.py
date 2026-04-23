"""Tests for envault.notify."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.notify import (
    add_notify,
    fire,
    load_notify,
    remove_notify,
    save_notify,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path: Path) -> None:
    assert load_notify(vault_path) == {}


def test_save_and_load_roundtrip(vault_path: Path) -> None:
    cfg = {"set": ["echo hello"], "unset": []}
    save_notify(vault_path, cfg)
    assert load_notify(vault_path) == cfg


def test_add_notify_creates_entry(vault_path: Path) -> None:
    add_notify(vault_path, "set", "echo set")
    cfg = load_notify(vault_path)
    assert "echo set" in cfg["set"]


def test_add_notify_idempotent(vault_path: Path) -> None:
    add_notify(vault_path, "set", "echo set")
    add_notify(vault_path, "set", "echo set")
    cfg = load_notify(vault_path)
    assert cfg["set"].count("echo set") == 1


def test_add_notify_multiple_commands(vault_path: Path) -> None:
    add_notify(vault_path, "rotate", "cmd_a")
    add_notify(vault_path, "rotate", "cmd_b")
    cfg = load_notify(vault_path)
    assert cfg["rotate"] == ["cmd_a", "cmd_b"]


def test_add_notify_unknown_event_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown event"):
        add_notify(vault_path, "explode", "rm -rf /")


def test_remove_notify_existing(vault_path: Path) -> None:
    add_notify(vault_path, "import", "notify_import")
    removed = remove_notify(vault_path, "import", "notify_import")
    assert removed is True
    assert "notify_import" not in load_notify(vault_path).get("import", [])


def test_remove_notify_missing_returns_false(vault_path: Path) -> None:
    removed = remove_notify(vault_path, "set", "ghost_cmd")
    assert removed is False


def test_fire_calls_commands(vault_path: Path) -> None:
    add_notify(vault_path, "set", "true")
    results = fire(vault_path, "set")
    assert results == [0]


def test_fire_passes_context_as_env(vault_path: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "out.txt"
    add_notify(vault_path, "set", f'sh -c \'echo $ENVAULT_KEY > {out_file}\'')
    fire(vault_path, "set", context={"key": "MY_VAR"})
    assert out_file.read_text().strip() == "MY_VAR"


def test_fire_returns_empty_list_when_no_commands(vault_path: Path) -> None:
    results = fire(vault_path, "expire")
    assert results == []
