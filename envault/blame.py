"""Blame: track which user/host last modified each key."""

from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blame_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".blame.json")


def load_blame(vault_path: Path) -> Dict[str, dict]:
    """Return the blame map: key -> {user, host, timestamp}."""
    path = _blame_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_blame(vault_path: Path, data: Dict[str, dict]) -> None:
    path = _blame_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def record_blame(
    vault_path: Path,
    key: str,
    *,
    user: Optional[str] = None,
    host: Optional[str] = None,
) -> dict:
    """Record that *key* was last touched by *user*@*host* right now."""
    if not key:
        raise ValueError("key must not be empty")
    data = load_blame(vault_path)
    entry = {
        "user": user or os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "host": host or socket.gethostname(),
        "timestamp": _now_iso(),
    }
    data[key] = entry
    save_blame(vault_path, data)
    return entry


def get_blame(vault_path: Path, key: str) -> Optional[dict]:
    """Return blame info for *key*, or None if not recorded."""
    return load_blame(vault_path).get(key)


def remove_blame(vault_path: Path, key: str) -> bool:
    """Remove blame entry for *key*. Returns True if it existed."""
    data = load_blame(vault_path)
    if key not in data:
        return False
    del data[key]
    save_blame(vault_path, data)
    return True


def format_blame(entry: dict) -> str:
    """Return a human-readable blame string."""
    return "{user}@{host} on {timestamp}".format(**entry)
