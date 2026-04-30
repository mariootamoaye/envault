"""Vault inheritance: resolve a key by walking a chain of profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.profile import vault_path_for_profile
from envault.store import VaultStore


@dataclass
class InheritResult:
    key: str
    value: Optional[str]
    resolved_from: Optional[str]  # profile name where value was found
    chain: List[str] = field(default_factory=list)  # full chain walked

    @property
    def found(self) -> bool:
        return self.value is not None


def resolve(
    key: str,
    chain: List[str],
    password: str,
    base_dir: Optional[Path] = None,
) -> InheritResult:
    """Walk *chain* (ordered most-specific first) and return the first
    profile that contains *key*.

    Parameters
    ----------
    key:       The env-var key to look up.
    chain:     Ordered list of profile names to search.
    password:  Decryption password (same for all profiles in the chain).
    base_dir:  Override the directory used for vault files (useful in tests).
    """
    for profile in chain:
        path = (
            base_dir / f"{profile}.vault"
            if base_dir
            else vault_path_for_profile(profile)
        )
        store = VaultStore(path, password)
        value = store.get(key)
        if value is not None:
            return InheritResult(
                key=key,
                value=value,
                resolved_from=profile,
                chain=list(chain),
            )
    return InheritResult(key=key, value=None, resolved_from=None, chain=list(chain))


def resolve_all(
    chain: List[str],
    password: str,
    base_dir: Optional[Path] = None,
) -> dict[str, InheritResult]:
    """Return a merged view of all keys across *chain*, with each key
    attributed to the most-specific (earliest) profile that defines it.
    """
    seen: dict[str, InheritResult] = {}
    for profile in reversed(chain):  # start from least-specific
        path = (
            base_dir / f"{profile}.vault"
            if base_dir
            else vault_path_for_profile(profile)
        )
        store = VaultStore(path, password)
        for key in store.keys():
            seen[key] = InheritResult(
                key=key,
                value=store.get(key),
                resolved_from=profile,
                chain=list(chain),
            )
    return seen
