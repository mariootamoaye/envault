"""Diff two vault profiles or a vault against a .env file."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from envault.store import VaultStore
from envault.import_env import parse_dotenv


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    left: Optional[str] = None
    right: Optional[str] = None


def diff_dicts(left: Dict[str, str], right: Dict[str, str]) -> List[DiffEntry]:
    """Compare two flat dicts and return a list of DiffEntry."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(left) | set(right))
    for key in all_keys:
        if key in left and key not in right:
            entries.append(DiffEntry(key=key, status="removed", left=left[key]))
        elif key not in left and key in right:
            entries.append(DiffEntry(key=key, status="added", right=right[key]))
        elif left[key] != right[key]:
            entries.append(DiffEntry(key=key, status="changed", left=left[key], right=right[key]))
        else:
            entries.append(DiffEntry(key=key, status="unchanged", left=left[key], right=right[key]))
    return entries


def diff_stores(store_a: VaultStore, password_a: str,
                store_b: VaultStore, password_b: str) -> List[DiffEntry]:
    left = {k: store_a.get(k, password_a) for k in store_a.keys()}
    right = {k: store_b.get(k, password_b) for k in store_b.keys()}
    return diff_dicts(left, right)


def diff_store_dotenv(store: VaultStore, password: str, dotenv_path: str) -> List[DiffEntry]:
    left = {k: store.get(k, password) for k in store.keys()}
    with open(dotenv_path) as fh:
        right = parse_dotenv(fh.read())
    return diff_dicts(left, right)


def format_diff(entries: List[DiffEntry], show_values: bool = False) -> str:
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for e in entries:
        sym = symbols[e.status]
        if show_values and e.status == "changed":
            lines.append(f"{sym} {e.key}  ({e.left!r} -> {e.right!r})")
        elif show_values and e.status == "added":
            lines.append(f"{sym} {e.key}={e.right!r}")
        elif show_values and e.status == "removed":
            lines.append(f"{sym} {e.key}={e.left!r}")
        else:
            lines.append(f"{sym} {e.key}")
    return "\n".join(lines)
