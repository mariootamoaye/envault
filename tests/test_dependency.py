"""Tests for envault.dependency."""

from pathlib import Path

import pytest

from envault.dependency import (
    add_dependency,
    all_dependencies,
    dependents_of,
    load_dependencies,
    remove_dependency,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_dependencies(vault_path) == {}


def test_add_dependency_creates_entry(vault_path):
    add_dependency(vault_path, key="APP_URL", depends_on="BASE_URL")
    deps = load_dependencies(vault_path)
    assert "APP_URL" in deps["BASE_URL"]


def test_add_dependency_is_idempotent(vault_path):
    add_dependency(vault_path, key="APP_URL", depends_on="BASE_URL")
    add_dependency(vault_path, key="APP_URL", depends_on="BASE_URL")
    deps = load_dependencies(vault_path)
    assert deps["BASE_URL"].count("APP_URL") == 1


def test_add_multiple_dependents(vault_path):
    add_dependency(vault_path, key="A", depends_on="ROOT")
    add_dependency(vault_path, key="B", depends_on="ROOT")
    assert set(dependents_of(vault_path, "ROOT")) == {"A", "B"}


def test_remove_dependency(vault_path):
    add_dependency(vault_path, key="A", depends_on="ROOT")
    add_dependency(vault_path, key="B", depends_on="ROOT")
    remove_dependency(vault_path, key="A", depends_on="ROOT")
    assert dependents_of(vault_path, "ROOT") == ["B"]


def test_remove_last_dependent_cleans_up_key(vault_path):
    add_dependency(vault_path, key="A", depends_on="ROOT")
    remove_dependency(vault_path, key="A", depends_on="ROOT")
    deps = load_dependencies(vault_path)
    assert "ROOT" not in deps


def test_remove_nonexistent_dependency_is_safe(vault_path):
    remove_dependency(vault_path, key="MISSING", depends_on="ROOT")


def test_dependents_of_returns_empty_for_unknown_key(vault_path):
    assert dependents_of(vault_path, "UNKNOWN") == []


def test_all_dependencies_reverse_lookup(vault_path):
    add_dependency(vault_path, key="CHILD", depends_on="PARENT_A")
    add_dependency(vault_path, key="CHILD", depends_on="PARENT_B")
    parents = all_dependencies(vault_path, "CHILD")
    assert set(parents) == {"PARENT_A", "PARENT_B"}


def test_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="key must not be empty"):
        add_dependency(vault_path, key="", depends_on="ROOT")


def test_empty_depends_on_raises(vault_path):
    with pytest.raises(ValueError, match="depends_on must not be empty"):
        add_dependency(vault_path, key="A", depends_on="")


def test_self_dependency_raises(vault_path):
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency(vault_path, key="A", depends_on="A")
