"""Policy enforcement for vault variables (required keys, value patterns)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _policy_path(vault_path: Path) -> Path:
    return vault_path.parent / "policy.json"


def load_policy(vault_path: Path) -> dict[str, Any]:
    """Load policy rules from disk, returning empty dict if not found."""
    path = _policy_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_policy(vault_path: Path, policy: dict[str, Any]) -> None:
    """Persist policy rules to disk."""
    _policy_path(vault_path).write_text(json.dumps(policy, indent=2))


def set_rule(vault_path: Path, key: str, *, required: bool | None = None, pattern: str | None = None) -> None:
    """Add or update a policy rule for a specific key."""
    policy = load_policy(vault_path)
    rule = policy.get(key, {})
    if required is not None:
        rule["required"] = required
    if pattern is not None:
        # Validate the pattern compiles
        re.compile(pattern)
        rule["pattern"] = pattern
    policy[key] = rule
    save_policy(vault_path, policy)


def remove_rule(vault_path: Path, key: str) -> bool:
    """Remove a policy rule. Returns True if it existed."""
    policy = load_policy(vault_path)
    if key not in policy:
        return False
    del policy[key]
    save_policy(vault_path, policy)
    return True


class PolicyViolation:
    def __init__(self, key: str, message: str) -> None:
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


def check_policy(vault_path: Path, store_keys: list[str], store_get) -> list[PolicyViolation]:
    """Evaluate all policy rules against the current vault contents."""
    policy = load_policy(vault_path)
    violations: list[PolicyViolation] = []

    for key, rule in policy.items():
        if rule.get("required", False) and key not in store_keys:
            violations.append(PolicyViolation(key, "required key is missing"))
            continue

        if "pattern" in rule and key in store_keys:
            value = store_get(key)
            if value is not None and not re.fullmatch(rule["pattern"], value):
                violations.append(
                    PolicyViolation(key, f"value does not match pattern '{rule['pattern']}'")
                )

    return violations
