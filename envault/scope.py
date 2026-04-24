"""Scope support: restrict keys to a named scope (e.g. 'ci', 'prod', 'local')."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

SCOPE_PREFIX = "__scope__:"


def _scope_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".scopes.json")


def load_scopes(vault_path: Path) -> Dict[str, str]:
    """Return {key: scope} mapping."""
    p = _scope_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_scopes(vault_path: Path, scopes: Dict[str, str]) -> None:
    p = _scope_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(scopes, indent=2))


def set_scope(vault_path: Path, key: str, scope: str) -> None:
    """Assign *key* to *scope*."""
    if not key:
        raise ValueError("key must not be empty")
    if not scope:
        raise ValueError("scope must not be empty")
    scopes = load_scopes(vault_path)
    scopes[key] = scope
    save_scopes(vault_path, scopes)


def remove_scope(vault_path: Path, key: str) -> bool:
    """Remove scope assignment for *key*. Returns True if it existed."""
    scopes = load_scopes(vault_path)
    if key not in scopes:
        return False
    del scopes[key]
    save_scopes(vault_path, scopes)
    return True


def keys_in_scope(vault_path: Path, scope: str) -> List[str]:
    """Return all keys assigned to *scope*."""
    return [k for k, s in load_scopes(vault_path).items() if s == scope]


def list_scopes(vault_path: Path) -> List[str]:
    """Return sorted list of unique scope names."""
    return sorted(set(load_scopes(vault_path).values()))


def filter_by_scope(
    data: Dict[str, str],
    vault_path: Path,
    scope: Optional[str],
) -> Dict[str, str]:
    """Return subset of *data* whose keys belong to *scope*.
    If *scope* is None the full dict is returned unchanged.
    """
    if scope is None:
        return data
    allowed = set(keys_in_scope(vault_path, scope))
    return {k: v for k, v in data.items() if k in allowed}
