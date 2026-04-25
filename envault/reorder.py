"""Key reordering and sorting utilities for vault entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envault.store import VaultStore


SORT_MODES = ("alpha", "alpha_desc", "length", "length_desc")


def sort_keys(
    data: dict[str, str],
    mode: str = "alpha",
) -> dict[str, str]:
    """Return a new dict with keys sorted according to *mode*.

    Modes
    -----
    alpha        – A → Z (default)
    alpha_desc   – Z → A
    length       – shortest key first
    length_desc  – longest key first
    """
    if mode not in SORT_MODES:
        raise ValueError(f"Unknown sort mode {mode!r}. Choose from: {SORT_MODES}")

    if mode == "alpha":
        ordered = sorted(data.keys())
    elif mode == "alpha_desc":
        ordered = sorted(data.keys(), reverse=True)
    elif mode == "length":
        ordered = sorted(data.keys(), key=len)
    else:  # length_desc
        ordered = sorted(data.keys(), key=len, reverse=True)

    return {k: data[k] for k in ordered}


def move_key(
    data: dict[str, str],
    key: str,
    position: int,
) -> dict[str, str]:
    """Return a new dict with *key* moved to *position* (0-based)."""
    if key not in data:
        raise KeyError(f"Key {key!r} not found in vault data.")
    keys = [k for k in data if k != key]
    position = max(0, min(position, len(keys)))
    keys.insert(position, key)
    return {k: data[k] for k in keys}


def reorder_store(store: "VaultStore", mode: str = "alpha") -> int:
    """Sort all keys in *store* in-place.  Returns the number of keys reordered."""
    raw = {k: store.get(k) for k in store.keys()}
    sorted_data = sort_keys(raw, mode=mode)
    for k in list(store.keys()):
        store.unset(k)
    for k, v in sorted_data.items():
        store.set(k, v)
    return len(sorted_data)
