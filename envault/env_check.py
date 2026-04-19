"""Check vault variables against the current environment."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import os


@dataclass
class CheckResult:
    key: str
    in_vault: bool
    in_env: bool
    match: bool  # True if env value equals vault value

    def status(self) -> str:
        if not self.in_env:
            return "missing"
        if not self.match:
            return "mismatch"
        return "ok"

    def __str__(self) -> str:
        return f"{self.key}: {self.status()}"


def check_env(vault_data: dict[str, str]) -> List[CheckResult]:
    """Compare vault keys/values against os.environ."""
    results = []
    for key, vault_value in sorted(vault_data.items()):
        in_env = key in os.environ
        env_value = os.environ.get(key)
        match = in_env and env_value == vault_value
        results.append(CheckResult(
            key=key,
            in_vault=True,
            in_env=in_env,
            match=match,
        ))
    return results


def summary(results: List[CheckResult]) -> dict[str, int]:
    """Return counts of each status in the results list."""
    counts: dict[str, int] = {"ok": 0, "missing": 0, "mismatch": 0}
    for r in results:
        counts[r.status()] += 1
    return counts


def format_check(results: List[CheckResult], show_ok: bool = True) -> str:
    lines = []
    icons = {"ok": "✓", "missing": "✗", "mismatch": "~"}
    for r in results:
        s = r.status()
        if s == "ok" and not show_ok:
            continue
        lines.append(f"{icons[s]}  {r}")
    return "\n".join(lines)
