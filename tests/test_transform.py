"""Tests for envault.transform."""
import pytest
from pathlib import Path
from envault.transform import (
    add_transform,
    remove_transforms,
    apply_transforms,
    apply_all,
    load_transforms,
    TransformError,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_transforms(vault_path) == {}


def test_add_transform_persists(vault_path):
    add_transform(vault_path, "API_KEY", "upper")
    data = load_transforms(vault_path)
    assert "API_KEY" in data
    assert data["API_KEY"][0]["op"] == "upper"


def test_add_multiple_transforms_ordered(vault_path):
    add_transform(vault_path, "VAR", "strip")
    add_transform(vault_path, "VAR", "upper")
    data = load_transforms(vault_path)
    ops = [s["op"] for s in data["VAR"]]
    assert ops == ["strip", "upper"]


def test_add_transform_empty_key_raises(vault_path):
    with pytest.raises(TransformError, match="empty"):
        add_transform(vault_path, "", "upper")


def test_add_transform_unknown_op_raises(vault_path):
    with pytest.raises(TransformError, match="unknown operation"):
        add_transform(vault_path, "KEY", "rot13")


def test_remove_transforms_returns_true(vault_path):
    add_transform(vault_path, "KEY", "lower")
    assert remove_transforms(vault_path, "KEY") is True
    assert load_transforms(vault_path) == {}


def test_remove_transforms_missing_key_returns_false(vault_path):
    assert remove_transforms(vault_path, "GHOST") is False


def test_apply_upper(vault_path):
    add_transform(vault_path, "K", "upper")
    assert apply_transforms(vault_path, "K", "hello") == "HELLO"


def test_apply_lower(vault_path):
    add_transform(vault_path, "K", "lower")
    assert apply_transforms(vault_path, "K", "WORLD") == "world"


def test_apply_strip(vault_path):
    add_transform(vault_path, "K", "strip")
    assert apply_transforms(vault_path, "K", "  hi  ") == "hi"


def test_apply_prefix(vault_path):
    add_transform(vault_path, "K", "prefix", "https://")
    assert apply_transforms(vault_path, "K", "example.com") == "https://example.com"


def test_apply_suffix(vault_path):
    add_transform(vault_path, "K", "suffix", "/v1")
    assert apply_transforms(vault_path, "K", "https://api") == "https://api/v1"


def test_apply_replace(vault_path):
    add_transform(vault_path, "K", "replace", "foo:bar")
    assert apply_transforms(vault_path, "K", "foo_baz") == "bar_baz"


def test_apply_no_transforms_returns_original(vault_path):
    assert apply_transforms(vault_path, "MISSING", "unchanged") == "unchanged"


def test_apply_all(vault_path):
    add_transform(vault_path, "A", "upper")
    add_transform(vault_path, "B", "lower")
    result = apply_all(vault_path, {"A": "hello", "B": "WORLD", "C": "keep"})
    assert result == {"A": "HELLO", "B": "world", "C": "keep"}
