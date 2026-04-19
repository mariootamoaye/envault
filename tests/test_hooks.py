"""Tests for envault.hooks."""
import json
import pytest
from pathlib import Path
from envault.hooks import (
    load_hooks,
    save_hooks,
    add_hook,
    remove_hook,
    fire,
    HOOK_FILE,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_load_hooks_returns_empty_when_no_file(vault_dir):
    assert load_hooks(vault_dir) == {}


def test_save_and_load_roundtrip(vault_dir):
    hooks = {"post-set": ["echo set"], "post-import": ["make reload"]}
    save_hooks(vault_dir, hooks)
    loaded = load_hooks(vault_dir)
    assert loaded == hooks


def test_save_rejects_unknown_event(vault_dir):
    with pytest.raises(ValueError, match="Unknown hook events"):
        save_hooks(vault_dir, {"on-magic": ["echo hi"]})


def test_add_hook_creates_entry(vault_dir):
    add_hook(vault_dir, "post-set", "echo hello")
    hooks = load_hooks(vault_dir)
    assert "echo hello" in hooks["post-set"]


def test_add_hook_no_duplicates(vault_dir):
    add_hook(vault_dir, "post-set", "echo hello")
    add_hook(vault_dir, "post-set", "echo hello")
    hooks = load_hooks(vault_dir)
    assert hooks["post-set"].count("echo hello") == 1


def test_add_hook_invalid_event(vault_dir):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(vault_dir, "on-magic", "echo hi")


def test_remove_hook_existing(vault_dir):
    add_hook(vault_dir, "pre-set", "echo before")
    removed = remove_hook(vault_dir, "pre-set", "echo before")
    assert removed is True
    hooks = load_hooks(vault_dir)
    assert "pre-set" not in hooks


def test_remove_hook_nonexistent(vault_dir):
    removed = remove_hook(vault_dir, "pre-set", "echo nope")
    assert removed is False


def test_fire_runs_commands(vault_dir, tmp_path):
    sentinel = tmp_path / "fired.txt"
    add_hook(vault_dir, "post-set", f"touch {sentinel}")
    codes = fire(vault_dir, "post-set")
    assert codes == [0]
    assert sentinel.exists()


def test_fire_no_hooks_returns_empty(vault_dir):
    codes = fire(vault_dir, "post-set")
    assert codes == []


def test_hooks_file_location(vault_dir):
    add_hook(vault_dir, "post-import", "make")
    assert (vault_dir / HOOK_FILE).exists()
