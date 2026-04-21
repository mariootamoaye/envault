"""Quota management: enforce limits on number of keys per vault/profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_QUOTA = 500
_QUOTA_FILENAME = ".quota.json"


def _quota_path(vault_dir: Path) -> Path:
    return vault_dir / _QUOTA_FILENAME


def load_quota(vault_dir: Path) -> dict:
    path = _quota_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_quota(vault_dir: Path, data: dict) -> None:
    path = _quota_path(vault_dir)
    vault_dir.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_quota(vault_dir: Path, limit: int) -> None:
    """Set the maximum number of keys allowed in this vault."""
    if limit < 1:
        raise ValueError(f"Quota limit must be >= 1, got {limit}")
    data = load_quota(vault_dir)
    data["limit"] = limit
    save_quota(vault_dir, data)


def get_quota(vault_dir: Path) -> int:
    """Return the configured quota limit, or the default."""
    data = load_quota(vault_dir)
    return data.get("limit", DEFAULT_QUOTA)


def remove_quota(vault_dir: Path) -> None:
    """Remove a custom quota, reverting to the default."""
    path = _quota_path(vault_dir)
    if path.exists():
        data = load_quota(vault_dir)
        data.pop("limit", None)
        save_quota(vault_dir, data)


def check_quota(vault_dir: Path, current_count: int, adding: int = 1) -> None:
    """Raise QuotaExceededError if adding `adding` keys would exceed the limit."""
    limit = get_quota(vault_dir)
    if current_count + adding > limit:
        raise QuotaExceededError(
            f"Quota exceeded: vault has {current_count} key(s), "
            f"limit is {limit}. Cannot add {adding} more."
        )


class QuotaExceededError(Exception):
    """Raised when an operation would exceed the configured key quota."""
