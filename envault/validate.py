"""Value validation rules for vault keys."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json

_VALID_TYPES = {"str", "int", "float", "bool", "url", "email", "regex"}


@dataclass
class ValidationError:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: [{self.rule}] {self.message}"


def _validate_path(vault_path: Path) -> Path:
    return vault_path.parent / ".envault_validate.json"


def load_rules(vault_path: Path) -> dict[str, dict[str, Any]]:
    p = _validate_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_rules(vault_path: Path, rules: dict[str, dict[str, Any]]) -> None:
    _validate_path(vault_path).write_text(json.dumps(rules, indent=2))


def set_rule(vault_path: Path, key: str, type_: str, pattern: str | None = None, required: bool = False) -> None:
    if not key:
        raise ValueError("key must not be empty")
    if type_ not in _VALID_TYPES:
        raise ValueError(f"unknown type '{type_}'; must be one of {sorted(_VALID_TYPES)}")
    rules = load_rules(vault_path)
    rules[key] = {"type": type_, "required": required}
    if pattern is not None:
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValueError(f"invalid regex pattern: {exc}") from exc
        rules[key]["pattern"] = pattern
    save_rules(vault_path, rules)


def remove_rule(vault_path: Path, key: str) -> bool:
    rules = load_rules(vault_path)
    if key not in rules:
        return False
    del rules[key]
    save_rules(vault_path, rules)
    return True


def validate_value(key: str, value: str, rule: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    type_ = rule.get("type", "str")
    if type_ == "int":
        try:
            int(value)
        except ValueError:
            errors.append(ValidationError(key, "type", f"expected int, got {value!r}"))
    elif type_ == "float":
        try:
            float(value)
        except ValueError:
            errors.append(ValidationError(key, "type", f"expected float, got {value!r}"))
    elif type_ == "bool":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            errors.append(ValidationError(key, "type", f"expected bool, got {value!r}"))
    elif type_ == "url":
        if not re.match(r"https?://", value, re.IGNORECASE):
            errors.append(ValidationError(key, "type", f"expected URL starting with http(s)://, got {value!r}"))
    elif type_ == "email":
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            errors.append(ValidationError(key, "type", f"expected email address, got {value!r}"))
    if "pattern" in rule:
        if not re.search(rule["pattern"], value):
            errors.append(ValidationError(key, "pattern", f"value does not match pattern {rule['pattern']!r}"))
    return errors


def validate_store(vault_path: Path, data: dict[str, str]) -> list[ValidationError]:
    rules = load_rules(vault_path)
    errors: list[ValidationError] = []
    for key, rule in rules.items():
        if rule.get("required") and key not in data:
            errors.append(ValidationError(key, "required", "key is required but missing"))
            continue
        if key in data:
            errors.extend(validate_value(key, data[key], rule))
    return errors
