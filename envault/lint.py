"""Lint vault keys and values for common issues."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List

_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')


@dataclass
class LintIssue:
    key: str
    severity: str  # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


def lint_keys(keys: list[str]) -> list[LintIssue]:
    """Check key naming conventions."""
    issues: list[LintIssue] = []
    for key in keys:
        if not key:
            issues.append(LintIssue(key="(empty)", severity="error", message="Key must not be empty"))
            continue
        if not _VALID_KEY_RE.match(key):
            issues.append(LintIssue(key=key, severity="warning",
                                     message="Key should be UPPER_SNAKE_CASE (A-Z, 0-9, _)"))
        if key.startswith('_'):
            issues.append(LintIssue(key=key, severity="warning",
                                     message="Key starts with underscore which is unconventional"))
    return issues


def lint_values(store_dict: dict[str, str]) -> list[LintIssue]:
    """Check values for potential issues."""
    issues: list[LintIssue] = []
    for key, value in store_dict.items():
        if value == "":
            issues.append(LintIssue(key=key, severity="warning", message="Value is empty"))
        if len(value) > 4096:
            issues.append(LintIssue(key=key, severity="warning",
                                     message=f"Value is very long ({len(value)} chars)"))
        if any(c in value for c in ('\n', '\r')):
            issues.append(LintIssue(key=key, severity="warning",
                                     message="Value contains newline characters"))
    return issues


def lint(store_dict: dict[str, str]) -> list[LintIssue]:
    """Run all lint checks and return combined issues."""
    return lint_keys(list(store_dict.keys())) + lint_values(store_dict)
