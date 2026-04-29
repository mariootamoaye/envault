"""Archive (soft-delete) keys without permanently removing them."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.audit import record as audit_record


def _archive_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".archive.json")


def load_archive(vault_path: Path) -> Dict[str, str]:
    """Return the archived key→value mapping (empty dict if none)."""
    path = _archive_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_archive(vault_path: Path, data: Dict[str, str]) -> None:
    path = _archive_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def archive_key(vault_path: Path, store, key: str) -> bool:
    """Move *key* from the live store into the archive.

    Returns True if the key existed and was archived, False otherwise.
    """
    value = store.get(key)
    if value is None:
        return False
    data = load_archive(vault_path)
    data[key] = value
    save_archive(vault_path, data)
    store.unset(key)
    store.save()
    audit_record(vault_path, "archive", key)
    return True


def restore_key(vault_path: Path, store, key: str) -> bool:
    """Move *key* from the archive back into the live store.

    Returns True if the key was in the archive, False otherwise.
    """
    data = load_archive(vault_path)
    if key not in data:
        return False
    store.set(key, data.pop(key))
    store.save()
    save_archive(vault_path, data)
    audit_record(vault_path, "restore", key)
    return True


def list_archived(vault_path: Path) -> List[str]:
    """Return a sorted list of archived key names."""
    return sorted(load_archive(vault_path).keys())


def purge_archive(vault_path: Path, key: Optional[str] = None) -> int:
    """Permanently delete archived keys.

    If *key* is given, only that key is purged; otherwise all are purged.
    Returns the number of keys removed.
    """
    data = load_archive(vault_path)
    if key is not None:
        if key in data:
            del data[key]
            save_archive(vault_path, data)
            return 1
        return 0
    count = len(data)
    save_archive(vault_path, {})
    return count
