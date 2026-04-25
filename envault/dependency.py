"""Track dependencies between environment variable keys.

Allows marking that one key depends on another, so that
changes or deletions can surface warnings about dependents.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _dep_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".deps.json")


def load_dependencies(vault_path: Path) -> Dict[str, List[str]]:
    """Return mapping of key -> list of keys that depend on it."""
    p = _dep_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_dependencies(vault_path: Path, deps: Dict[str, List[str]]) -> None:
    p = _dep_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(deps, indent=2))


def add_dependency(vault_path: Path, key: str, depends_on: str) -> None:
    """Record that *key* depends on *depends_on*."""
    if not key:
        raise ValueError("key must not be empty")
    if not depends_on:
        raise ValueError("depends_on must not be empty")
    if key == depends_on:
        raise ValueError("a key cannot depend on itself")
    deps = load_dependencies(vault_path)
    dependents = deps.setdefault(depends_on, [])
    if key not in dependents:
        dependents.append(key)
    save_dependencies(vault_path, deps)


def remove_dependency(vault_path: Path, key: str, depends_on: str) -> None:
    """Remove the dependency record of *key* on *depends_on*."""
    deps = load_dependencies(vault_path)
    if depends_on in deps:
        deps[depends_on] = [k for k in deps[depends_on] if k != key]
        if not deps[depends_on]:
            del deps[depends_on]
    save_dependencies(vault_path, deps)


def dependents_of(vault_path: Path, key: str) -> List[str]:
    """Return list of keys that depend on *key*."""
    deps = load_dependencies(vault_path)
    return list(deps.get(key, []))


def all_dependencies(vault_path: Path, key: str) -> List[str]:
    """Return all keys that *key* depends on (reverse lookup)."""
    deps = load_dependencies(vault_path)
    return [parent for parent, children in deps.items() if key in children]
