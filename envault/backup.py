"""Backup and restore vault files to/from a compressed archive."""

import gzip
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path


def _now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def backup_vault(vault_path: Path, backup_dir: Path) -> Path:
    """Create a gzipped backup of the vault file.

    Returns the path to the created backup file.
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = _now_stamp()
    backup_name = f"vault_backup_{stamp}.json.gz"
    dest = backup_dir / backup_name

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    with open(vault_path, "rb") as src_fh:
        data = src_fh.read()

    with gzip.open(dest, "wb") as gz_fh:
        gz_fh.write(data)

    return dest


def restore_vault(backup_path: Path, vault_path: Path) -> None:
    """Restore a vault file from a gzipped backup.

    Overwrites the existing vault file.
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")

    with gzip.open(backup_path, "rb") as gz_fh:
        data = gz_fh.read()

    # Validate it's parseable JSON before overwriting.
    try:
        json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Backup contains invalid JSON: {exc}") from exc

    vault_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vault_path, "wb") as dst_fh:
        dst_fh.write(data)


def list_backups(backup_dir: Path) -> list[Path]:
    """Return backup files sorted newest-first."""
    if not backup_dir.exists():
        return []
    files = sorted(
        backup_dir.glob("vault_backup_*.json.gz"),
        key=lambda p: p.name,
        reverse=True,
    )
    return files


def delete_backup(backup_path: Path) -> None:
    """Delete a single backup file."""
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")
    backup_path.unlink()
