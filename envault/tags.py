"""Tag-based grouping for vault keys."""
from __future__ import annotations

META_PREFIX = "__tags__."


def _tag_key(var_key: str) -> str:
    return f"{META_PREFIX}{var_key}"


def set_tags(store, var_key: str, tags: list[str]) -> None:
    """Associate tags with a vault key."""
    store.set(_tag_key(var_key), ",".join(sorted(set(tags))))


def get_tags(store, var_key: str) -> list[str]:
    """Return tags for a vault key, or empty list."""
    raw = store.get(_tag_key(var_key))
    if not raw:
        return []
    return [t for t in raw.split(",") if t]


def remove_tags(store, var_key: str) -> None:
    """Remove tag metadata for a vault key."""
    tk = _tag_key(var_key)
    try:
        store.unset(tk)
    except KeyError:
        pass


def keys_by_tag(store, tag: str) -> list[str]:
    """Return all vault keys that have the given tag."""
    results = []
    for k in store.keys():
        if k.startswith(META_PREFIX):
            continue
        if tag in get_tags(store, k):
            results.append(k)
    return sorted(results)


def all_tags(store) -> dict[str, list[str]]:
    """Return mapping of var_key -> tags for all keys that have tags."""
    out: dict[str, list[str]] = {}
    for k in store.keys():
        if k.startswith(META_PREFIX):
            continue
        tags = get_tags(store, k)
        if tags:
            out[k] = tags
    return out
