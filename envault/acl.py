"""Access control lists: restrict which keys a given user/role can read or write."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_ACL_FILENAME = ".envault_acl.json"


def _acl_path(vault_dir: Path) -> Path:
    return vault_dir / _ACL_FILENAME


def load_acl(vault_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    """Return ACL mapping: {role: {"read": [...], "write": [...]}}."""
    path = _acl_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_acl(vault_dir: Path, acl: Dict[str, Dict[str, List[str]]]) -> None:
    path = _acl_path(vault_dir)
    path.write_text(json.dumps(acl, indent=2))


def set_permission(
    vault_dir: Path,
    role: str,
    action: str,
    keys: List[str],
) -> None:
    """Set the allowed keys for *role* and *action* ('read' or 'write')."""
    if action not in ("read", "write"):
        raise ValueError(f"action must be 'read' or 'write', got {action!r}")
    acl = load_acl(vault_dir)
    acl.setdefault(role, {})[action] = list(keys)
    save_acl(vault_dir, acl)


def remove_role(vault_dir: Path, role: str) -> None:
    """Remove a role entirely from the ACL."""
    acl = load_acl(vault_dir)
    acl.pop(role, None)
    save_acl(vault_dir, acl)


def can_access(vault_dir: Path, role: str, action: str, key: str) -> bool:
    """Return True if *role* is allowed to perform *action* on *key*.

    An empty list means no keys are permitted.  A missing role/action entry
    is treated as *deny*.
    """
    acl = load_acl(vault_dir)
    allowed: Optional[List[str]] = acl.get(role, {}).get(action)
    if allowed is None:
        return False
    return key in allowed


def list_roles(vault_dir: Path) -> List[str]:
    """Return all defined role names."""
    return list(load_acl(vault_dir).keys())
