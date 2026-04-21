"""Key expiry scheduling: set absolute expiry dates on vault keys."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_EXPIRY_FILE = ".expiry.json"


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _expiry_path(vault_path: Path) -> Path:
    return vault_path.parent / _EXPIRY_FILE


def load_expiry(vault_path: Path) -> Dict[str, str]:
    """Return mapping of key -> ISO-8601 expiry datetime string."""
    path = _expiry_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_expiry(vault_path: Path, data: Dict[str, str]) -> None:
    path = _expiry_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: Path, key: str, expires_at: datetime) -> None:
    """Attach an expiry datetime to *key*."""
    data = load_expiry(vault_path)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    save_expiry(vault_path, data)


def remove_expiry(vault_path: Path, key: str) -> None:
    """Remove any expiry entry for *key*."""
    data = load_expiry(vault_path)
    data.pop(key, None)
    save_expiry(vault_path, data)


def get_expiry(vault_path: Path, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or None if unset."""
    data = load_expiry(vault_path)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(vault_path: Path, key: str) -> bool:
    """Return True when *key* has passed its expiry datetime."""
    expiry = get_expiry(vault_path, key)
    if expiry is None:
        return False
    return _now() >= expiry


def expired_keys(vault_path: Path) -> List[str]:
    """Return all keys whose expiry has passed."""
    data = load_expiry(vault_path)
    now = _now()
    return [
        k for k, v in data.items()
        if now >= datetime.fromisoformat(v)
    ]


def purge_expired(vault_path: Path, store) -> List[str]:
    """Delete all expired keys from *store* and remove their expiry entries.

    Returns the list of purged key names.
    """
    keys = expired_keys(vault_path)
    for k in keys:
        store.unset(k)
        remove_expiry(vault_path, k)
    return keys
