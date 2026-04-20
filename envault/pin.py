"""Pin specific vault keys to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_PIN_FILENAME = ".pins.json"


def _pin_path(vault_dir: Path) -> Path:
    return vault_dir / _PIN_FILENAME


def load_pins(vault_dir: Path) -> List[str]:
    """Return the list of pinned keys for the given vault directory."""
    path = _pin_path(vault_dir)
    if not path.exists():
        return []
    with path.open() as fh:
        data = json.load(fh)
    return data.get("pins", [])


def save_pins(vault_dir: Path, pins: List[str]) -> None:
    """Persist the list of pinned keys."""
    path = _pin_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump({"pins": sorted(set(pins))}, fh, indent=2)


def pin_key(vault_dir: Path, key: str) -> None:
    """Add *key* to the pinned set.  No-op if already pinned."""
    if not key:
        raise ValueError("key must not be empty")
    pins = load_pins(vault_dir)
    if key not in pins:
        pins.append(key)
        save_pins(vault_dir, pins)


def unpin_key(vault_dir: Path, key: str) -> None:
    """Remove *key* from the pinned set.  No-op if not pinned."""
    pins = load_pins(vault_dir)
    updated = [p for p in pins if p != key]
    if len(updated) != len(pins):
        save_pins(vault_dir, updated)


def is_pinned(vault_dir: Path, key: str) -> bool:
    """Return True if *key* is currently pinned."""
    return key in load_pins(vault_dir)


def assert_not_pinned(vault_dir: Path, key: str) -> None:
    """Raise RuntimeError if *key* is pinned, to guard mutation operations."""
    if is_pinned(vault_dir, key):
        raise RuntimeError(
            f"Key '{key}' is pinned and cannot be modified or deleted. "
            "Use 'envault pin unpin {key}' to remove the pin first."
        )
