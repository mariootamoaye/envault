"""merge.py — utilities for merging multiple vault profiles or dicts.

Supports different merge strategies:
  - 'last_wins'  : later sources overwrite earlier ones (default)
  - 'first_wins' : earlier sources take priority
  - 'error'      : raise on any key conflict
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from envault.store import VaultStore

MergeStrategy = Literal["last_wins", "first_wins", "error"]


class MergeConflictError(Exception):
    """Raised when 'error' strategy encounters a duplicate key."""

    def __init__(self, key: str, sources: List[str]) -> None:
        self.key = key
        self.sources = sources
        super().__init__(
            f"Merge conflict: key '{key}' appears in multiple sources: "
            + ", ".join(sources)
        )


@dataclass
class MergeResult:
    """Result of a merge operation."""

    data: Dict[str, str] = field(default_factory=dict)
    # Maps each key to the source label it came from
    sources: Dict[str, str] = field(default_factory=dict)
    # Keys that were overwritten (only populated for 'last_wins')
    overwritten: Dict[str, List[str]] = field(default_factory=dict)


def merge_dicts(
    sources: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
    strategy: MergeStrategy = "last_wins",
) -> MergeResult:
    """Merge a list of plain dicts into a single MergeResult.

    Args:
        sources:  Ordered list of key→value dicts to merge.
        labels:   Human-readable name for each source (used in conflict info).
                  Defaults to "source_0", "source_1", …
        strategy: How to handle duplicate keys.

    Returns:
        A MergeResult with the merged data and provenance information.
    """
    if labels is None:
        labels = [f"source_{i}" for i in range(len(sources))]

    if len(labels) != len(sources):
        raise ValueError("'labels' length must match 'sources' length")

    result = MergeResult()

    for label, src in zip(labels, sources):
        for key, value in src.items():
            if key in result.data:
                existing_label = result.sources[key]
                if strategy == "error":
                    raise MergeConflictError(key, [existing_label, label])
                elif strategy == "first_wins":
                    # Record that this source was skipped for this key
                    result.overwritten.setdefault(key, []).append(label)
                    continue
                else:  # last_wins
                    result.overwritten.setdefault(key, []).append(existing_label)

            result.data[key] = value
            result.sources[key] = label

    return result


def merge_stores(
    stores: List[VaultStore],
    password: str,
    labels: Optional[List[str]] = None,
    strategy: MergeStrategy = "last_wins",
) -> MergeResult:
    """Merge multiple VaultStore instances into a single MergeResult.

    Each store is decrypted with *password* before merging.

    Args:
        stores:   Ordered list of VaultStore objects.
        password: Decryption password (must be valid for every store).
        labels:   Optional human-readable names for each store.
        strategy: Merge strategy — 'last_wins', 'first_wins', or 'error'.

    Returns:
        A MergeResult containing the merged environment variables.
    """
    dicts: List[Dict[str, str]] = []
    for store in stores:
        dicts.append({k: store.get(k, password) for k in store.keys()})

    return merge_dicts(dicts, labels=labels, strategy=strategy)


def apply_merge(target: VaultStore, result: MergeResult, password: str) -> int:
    """Write all keys from a MergeResult into *target* store.

    Args:
        target:   The VaultStore to write into.
        result:   A MergeResult produced by merge_dicts or merge_stores.
        password: Encryption password for the target store.

    Returns:
        Number of keys written.
    """
    for key, value in result.data.items():
        target.set(key, value, password)
    return len(result.data)
