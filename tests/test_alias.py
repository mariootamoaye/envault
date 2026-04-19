"""Tests for envault.alias."""
import pytest
from pathlib import Path
from envault.alias import (
    add_alias,
    remove_alias,
    resolve,
    list_aliases,
    load_aliases,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vault"


def test_load_aliases_returns_empty_when_no_file(vault_dir):
    assert load_aliases(vault_dir) == {}


def test_add_alias_creates_mapping(vault_dir):
    add_alias(vault_dir, "db", "DATABASE_URL")
    assert load_aliases(vault_dir) == {"db": "DATABASE_URL"}


def test_add_alias_overwrites_existing(vault_dir):
    add_alias(vault_dir, "db", "DATABASE_URL")
    add_alias(vault_dir, "db", "POSTGRES_URL")
    assert load_aliases(vault_dir)["db"] == "POSTGRES_URL"


def test_add_alias_empty_alias_raises(vault_dir):
    with pytest.raises(ValueError, match="alias"):
        add_alias(vault_dir, "", "DATABASE_URL")


def test_add_alias_empty_key_raises(vault_dir):
    with pytest.raises(ValueError, match="key"):
        add_alias(vault_dir, "db", "")


def test_remove_alias_returns_true_when_found(vault_dir):
    add_alias(vault_dir, "db", "DATABASE_URL")
    assert remove_alias(vault_dir, "db") is True
    assert "db" not in load_aliases(vault_dir)


def test_remove_alias_returns_false_when_missing(vault_dir):
    assert remove_alias(vault_dir, "nope") is False


def test_resolve_returns_key_for_known_alias(vault_dir):
    add_alias(vault_dir, "db", "DATABASE_URL")
    assert resolve(vault_dir, "db") == "DATABASE_URL"


def test_resolve_returns_name_unchanged_when_no_alias(vault_dir):
    assert resolve(vault_dir, "DATABASE_URL") == "DATABASE_URL"


def test_list_aliases_returns_all(vault_dir):
    add_alias(vault_dir, "db", "DATABASE_URL")
    add_alias(vault_dir, "secret", "SECRET_KEY")
    result = list_aliases(vault_dir)
    assert result == {"db": "DATABASE_URL", "secret": "SECRET_KEY"}
