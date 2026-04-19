"""Key aliasing — map a short alias to a vault key."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_ALIAS_FILE = ".envault_aliases.json"


def _alias_path(vault_dir: Path) -> Path:
    return vault_dir / _ALIAS_FILE


def load_aliases(vault_dir: Path) -> Dict[str, str]:
    """Return alias->key mapping, or empty dict if none saved."""
    p = _alias_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_aliases(vault_dir: Path, aliases: Dict[str, str]) -> None:
    vault_dir.mkdir(parents=True, exist_ok=True)
    _alias_path(vault_dir).write_text(json.dumps(aliases, indent=2))


def add_alias(vault_dir: Path, alias: str, key: str) -> None:
    """Create or overwrite *alias* pointing to *key*."""
    if not alias:
        raise ValueError("alias must not be empty")
    if not key:
        raise ValueError("key must not be empty")
    aliases = load_aliases(vault_dir)
    aliases[alias] = key
    save_aliases(vault_dir, aliases)


def remove_alias(vault_dir: Path, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed."""
    aliases = load_aliases(vault_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    save_aliases(vault_dir, aliases)
    return True


def resolve(vault_dir: Path, name: str) -> str:
    """Return the real key for *name*, following at most one level of aliasing."""
    aliases = load_aliases(vault_dir)
    return aliases.get(name, name)


def list_aliases(vault_dir: Path) -> Dict[str, str]:
    return load_aliases(vault_dir)
