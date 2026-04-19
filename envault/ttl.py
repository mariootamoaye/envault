"""TTL (time-to-live) support for vault entries."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional


TTL_META_PREFIX = "__ttl__"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def set_ttl(store, key: str, seconds: int) -> None:
    """Record an expiry timestamp for *key* in the store."""
    expiry = _now() + timedelta(seconds=seconds)
    meta_key = TTL_META_PREFIX + key
    store.set(meta_key, expiry.isoformat())


def get_expiry(store, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or None if no TTL is set."""
    meta_key = TTL_META_PREFIX + key
    raw = store.get(meta_key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(store, key: str) -> bool:
    """Return True if *key* has a TTL that has passed."""
    expiry = get_expiry(store, key)
    if expiry is None:
        return False
    return _now() >= expiry


def purge_expired(store) -> list[str]:
    """Remove all expired keys (and their TTL metadata) from the store.

    Returns the list of purged keys.
    """
    purged: list[str] = []
    # collect real keys (not meta keys)
    all_keys = [k for k in store.list() if not k.startswith(TTL_META_PREFIX)]
    for key in all_keys:
        if is_expired(store, key):
            store.unset(key)
            meta_key = TTL_META_PREFIX + key
            try:
                store.unset(meta_key)
            except KeyError:
                pass
            purged.append(key)
    return purged


def clear_ttl(store, key: str) -> None:
    """Remove TTL metadata for *key* without deleting the key itself."""
    meta_key = TTL_META_PREFIX + key
    try:
        store.unset(meta_key)
    except KeyError:
        pass
