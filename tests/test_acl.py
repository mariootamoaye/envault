"""Tests for envault.acl."""

from pathlib import Path

import pytest

from envault.acl import (
    can_access,
    list_roles,
    load_acl,
    remove_role,
    set_permission,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_returns_empty_when_no_file(vault_dir):
    assert load_acl(vault_dir) == {}


def test_set_permission_creates_role(vault_dir):
    set_permission(vault_dir, "developer", "read", ["DB_URL", "API_KEY"])
    acl = load_acl(vault_dir)
    assert "developer" in acl
    assert acl["developer"]["read"] == ["DB_URL", "API_KEY"]


def test_set_permission_overwrites_existing(vault_dir):
    set_permission(vault_dir, "developer", "read", ["DB_URL"])
    set_permission(vault_dir, "developer", "read", ["API_KEY"])
    acl = load_acl(vault_dir)
    assert acl["developer"]["read"] == ["API_KEY"]


def test_set_permission_invalid_action_raises(vault_dir):
    with pytest.raises(ValueError, match="action must be"):
        set_permission(vault_dir, "admin", "execute", ["SECRET"])


def test_can_access_returns_true_when_allowed(vault_dir):
    set_permission(vault_dir, "ops", "write", ["DB_PASSWORD"])
    assert can_access(vault_dir, "ops", "write", "DB_PASSWORD") is True


def test_can_access_returns_false_when_key_not_listed(vault_dir):
    set_permission(vault_dir, "ops", "read", ["DB_URL"])
    assert can_access(vault_dir, "ops", "read", "SECRET_KEY") is False


def test_can_access_returns_false_for_unknown_role(vault_dir):
    assert can_access(vault_dir, "ghost", "read", "ANY_KEY") is False


def test_can_access_returns_false_for_missing_action(vault_dir):
    set_permission(vault_dir, "dev", "read", ["TOKEN"])
    assert can_access(vault_dir, "dev", "write", "TOKEN") is False


def test_remove_role_deletes_entry(vault_dir):
    set_permission(vault_dir, "ci", "read", ["CI_TOKEN"])
    remove_role(vault_dir, "ci")
    assert "ci" not in load_acl(vault_dir)


def test_remove_role_nonexistent_is_noop(vault_dir):
    remove_role(vault_dir, "nobody")  # should not raise


def test_list_roles_returns_all_roles(vault_dir):
    set_permission(vault_dir, "admin", "write", ["X"])
    set_permission(vault_dir, "viewer", "read", ["X"])
    roles = list_roles(vault_dir)
    assert set(roles) == {"admin", "viewer"}
