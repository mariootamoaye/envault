"""Tests for envault.validate."""
import pytest
from pathlib import Path
from envault.validate import (
    load_rules,
    set_rule,
    remove_rule,
    validate_value,
    validate_store,
    ValidationError,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_rules(vault_path) == {}


def test_set_rule_persists(vault_path):
    set_rule(vault_path, "PORT", "int")
    rules = load_rules(vault_path)
    assert "PORT" in rules
    assert rules["PORT"]["type"] == "int"


def test_set_rule_with_pattern(vault_path):
    set_rule(vault_path, "COLOR", "str", pattern=r"^#[0-9a-fA-F]{6}$")
    rules = load_rules(vault_path)
    assert rules["COLOR"]["pattern"] == r"^#[0-9a-fA-F]{6}$"


def test_set_rule_invalid_type_raises(vault_path):
    with pytest.raises(ValueError, match="unknown type"):
        set_rule(vault_path, "KEY", "uuid")


def test_set_rule_invalid_pattern_raises(vault_path):
    with pytest.raises(ValueError, match="invalid regex"):
        set_rule(vault_path, "KEY", "str", pattern="[unclosed")


def test_set_rule_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="must not be empty"):
        set_rule(vault_path, "", "str")


def test_remove_rule_existing(vault_path):
    set_rule(vault_path, "API_KEY", "str")
    assert remove_rule(vault_path, "API_KEY") is True
    assert load_rules(vault_path) == {}


def test_remove_rule_missing(vault_path):
    assert remove_rule(vault_path, "MISSING") is False


def test_validate_value_int_ok():
    assert validate_value("PORT", "8080", {"type": "int"}) == []


def test_validate_value_int_fail():
    errs = validate_value("PORT", "abc", {"type": "int"})
    assert len(errs) == 1
    assert errs[0].rule == "type"


def test_validate_value_bool_ok():
    for v in ("true", "false", "1", "0", "yes", "no", "True", "YES"):
        assert validate_value("FLAG", v, {"type": "bool"}) == []


def test_validate_value_url_ok():
    assert validate_value("URL", "https://example.com", {"type": "url"}) == []


def test_validate_value_url_fail():
    errs = validate_value("URL", "ftp://bad", {"type": "url"})
    assert errs[0].rule == "type"


def test_validate_value_email_ok():
    assert validate_value("MAIL", "user@example.com", {"type": "email"}) == []


def test_validate_value_email_fail():
    errs = validate_value("MAIL", "not-an-email", {"type": "email"})
    assert errs[0].rule == "type"


def test_validate_value_pattern_fail():
    errs = validate_value("COLOR", "red", {"type": "str", "pattern": r"^#[0-9a-fA-F]{6}$"})
    assert errs[0].rule == "pattern"


def test_validate_store_required_missing(vault_path):
    set_rule(vault_path, "DATABASE_URL", "url", required=True)
    errs = validate_store(vault_path, {})
    assert any(e.rule == "required" for e in errs)


def test_validate_store_required_present(vault_path):
    set_rule(vault_path, "DATABASE_URL", "url", required=True)
    errs = validate_store(vault_path, {"DATABASE_URL": "https://db.example.com"})
    assert errs == []


def test_validate_store_type_error(vault_path):
    set_rule(vault_path, "PORT", "int")
    errs = validate_store(vault_path, {"PORT": "not-a-number"})
    assert errs[0].key == "PORT"


def test_validation_error_str():
    e = ValidationError("PORT", "type", "expected int")
    assert "PORT" in str(e)
    assert "type" in str(e)
    assert "expected int" in str(e)
