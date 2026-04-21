"""Tests for envault.policy module."""

import pytest
from pathlib import Path
from envault.policy import (
    load_policy,
    save_policy,
    set_rule,
    remove_rule,
    check_policy,
    PolicyViolation,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_policy(vault_path) == {}


def test_set_rule_required(vault_path):
    set_rule(vault_path, "DATABASE_URL", required=True)
    policy = load_policy(vault_path)
    assert policy["DATABASE_URL"]["required"] is True


def test_set_rule_pattern(vault_path):
    set_rule(vault_path, "PORT", pattern=r"\d+")
    policy = load_policy(vault_path)
    assert policy["PORT"]["pattern"] == r"\d+"


def test_set_rule_invalid_pattern_raises(vault_path):
    import re
    with pytest.raises(re.error):
        set_rule(vault_path, "KEY", pattern="[invalid")


def test_set_rule_updates_existing(vault_path):
    set_rule(vault_path, "API_KEY", required=True)
    set_rule(vault_path, "API_KEY", pattern=r".{16,}")
    policy = load_policy(vault_path)
    assert policy["API_KEY"]["required"] is True
    assert policy["API_KEY"]["pattern"] == r".{16,}"


def test_remove_rule_existing(vault_path):
    set_rule(vault_path, "SECRET", required=True)
    result = remove_rule(vault_path, "SECRET")
    assert result is True
    assert "SECRET" not in load_policy(vault_path)


def test_remove_rule_nonexistent(vault_path):
    result = remove_rule(vault_path, "MISSING")
    assert result is False


def test_check_policy_missing_required(vault_path):
    set_rule(vault_path, "DATABASE_URL", required=True)
    violations = check_policy(vault_path, [], lambda k: None)
    assert len(violations) == 1
    assert violations[0].key == "DATABASE_URL"
    assert "missing" in violations[0].message


def test_check_policy_pattern_match(vault_path):
    set_rule(vault_path, "PORT", pattern=r"\d+")
    violations = check_policy(vault_path, ["PORT"], lambda k: "8080")
    assert violations == []


def test_check_policy_pattern_mismatch(vault_path):
    set_rule(vault_path, "PORT", pattern=r"\d+")
    violations = check_policy(vault_path, ["PORT"], lambda k: "not-a-port")
    assert len(violations) == 1
    assert "pattern" in violations[0].message


def test_check_policy_no_violations(vault_path):
    set_rule(vault_path, "API_KEY", required=True)
    violations = check_policy(vault_path, ["API_KEY"], lambda k: "somevalue")
    assert violations == []


def test_policy_violation_str(vault_path):
    v = PolicyViolation("MY_KEY", "required key is missing")
    assert str(v) == "MY_KEY: required key is missing"
