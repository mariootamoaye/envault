"""Promote variables from one profile to another, with optional key filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.store import VaultStore


@dataclass
class PromoteResult:
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.promoted) + len(self.overwritten)


def promote(
    src: VaultStore,
    dst: VaultStore,
    password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> PromoteResult:
    """Copy variables from *src* vault into *dst* vault.

    Args:
        src: Source vault (already unlocked via its own password).
        dst: Destination vault.
        password: Password used to *write* values into *dst*.
        keys: Optional allowlist of keys to promote. Promotes all if None.
        overwrite: When True, existing keys in *dst* are overwritten.
        dry_run: When True, no writes are performed.

    Returns:
        A :class:`PromoteResult` summarising what happened.
    """
    result = PromoteResult()

    candidate_keys = keys if keys is not None else src.keys()

    for key in candidate_keys:
        value = src.get(key)
        if value is None:
            result.skipped.append(key)
            continue

        already_exists = dst.get(key) is not None

        if already_exists and not overwrite:
            result.skipped.append(key)
            continue

        if not dry_run:
            dst.set(key, value, password)

        if already_exists:
            result.overwritten.append(key)
        else:
            result.promoted.append(key)

    return result
