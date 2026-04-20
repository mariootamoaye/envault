"""Track change history for vault keys."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _history_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".history.json")


def record_change(
    vault_path: Path,
    key: str,
    action: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
) -> None:
    """Append a change entry for a key."""
    path = _history_path(vault_path)
    entries = read_history(vault_path)
    entries.append(
        {
            "ts": _now_iso(),
            "key": key,
            "action": action,
            "old": old_value,
            "new": new_value,
        }
    )
    path.write_text(json.dumps(entries, indent=2))


def read_history(vault_path: Path) -> List[Dict[str, Any]]:
    """Return all history entries for a vault."""
    path = _history_path(vault_path)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def key_history(vault_path: Path, key: str) -> List[Dict[str, Any]]:
    """Return history entries filtered to a specific key."""
    return [e for e in read_history(vault_path) if e["key"] == key]


def clear_history(vault_path: Path) -> None:
    """Delete the history file."""
    path = _history_path(vault_path)
    if path.exists():
        path.unlink()
