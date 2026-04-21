"""Checksum utilities for detecting vault tampering or drift."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

_CHECKSUM_FILENAME = ".vault_checksum"


def _checksum_path(vault_path: Path) -> Path:
    return vault_path.parent / _CHECKSUM_FILENAME


def compute_checksum(data: Dict[str, str]) -> str:
    """Return a SHA-256 hex digest of the canonical JSON representation of data."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def save_checksum(vault_path: Path, checksum: str) -> None:
    """Persist a checksum string next to the vault file."""
    _checksum_path(vault_path).write_text(checksum)


def load_checksum(vault_path: Path) -> Optional[str]:
    """Load the stored checksum, or None if it does not exist."""
    path = _checksum_path(vault_path)
    if not path.exists():
        return None
    return path.read_text().strip()


def verify(vault_path: Path, data: Dict[str, str]) -> bool:
    """Return True if the stored checksum matches the current data."""
    stored = load_checksum(vault_path)
    if stored is None:
        return False
    return stored == compute_checksum(data)


def update(vault_path: Path, data: Dict[str, str]) -> str:
    """Recompute and persist the checksum for data; return the new checksum."""
    checksum = compute_checksum(data)
    save_checksum(vault_path, checksum)
    return checksum


def delete_checksum(vault_path: Path) -> None:
    """Remove the stored checksum file if it exists."""
    path = _checksum_path(vault_path)
    if path.exists():
        path.unlink()
