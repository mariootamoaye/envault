"""Track deprecated keys and warn when they are accessed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_FILENAME = ".envault_deprecated.json"


def _deprecate_path(vault_path: Path) -> Path:
    return vault_path.parent / _FILENAME


def load_deprecated(vault_path: Path) -> Dict[str, dict]:
    """Return mapping of key -> {reason, replacement}."""
    p = _deprecate_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_deprecated(vault_path: Path, data: Dict[str, dict]) -> None:
    p = _deprecate_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def mark_deprecated(
    vault_path: Path,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> None:
    """Mark *key* as deprecated, optionally pointing to a replacement."""
    if not key:
        raise ValueError("key must not be empty")
    data = load_deprecated(vault_path)
    data[key] = {"reason": reason, "replacement": replacement}
    save_deprecated(vault_path, data)


def unmark_deprecated(vault_path: Path, key: str) -> bool:
    """Remove deprecation mark from *key*. Returns True if it existed."""
    data = load_deprecated(vault_path)
    if key not in data:
        return False
    del data[key]
    save_deprecated(vault_path, data)
    return True


def is_deprecated(vault_path: Path, key: str) -> bool:
    return key in load_deprecated(vault_path)


def deprecation_warning(vault_path: Path, key: str) -> Optional[str]:
    """Return a human-readable warning string for *key*, or None."""
    data = load_deprecated(vault_path)
    if key not in data:
        return None
    entry = data[key]
    msg = f"Key '{key}' is deprecated."
    if entry.get("reason"):
        msg += f" Reason: {entry['reason']}."
    if entry.get("replacement"):
        msg += f" Use '{entry['replacement']}' instead."
    return msg
