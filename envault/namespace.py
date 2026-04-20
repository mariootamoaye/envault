"""Namespace support for grouping vault keys under logical prefixes."""

from __future__ import annotations

SEPARATOR = "__"


def make_key(namespace: str, key: str) -> str:
    """Combine a namespace and a key into a namespaced key."""
    if not namespace:
        raise ValueError("namespace must not be empty")
    if not key:
        raise ValueError("key must not be empty")
    return f"{namespace.upper()}{SEPARATOR}{key.upper()}"


def split_key(namespaced_key: str) -> tuple[str, str]:
    """Split a namespaced key into (namespace, key). Raises ValueError if no separator."""
    if SEPARATOR not in namespaced_key:
        raise ValueError(f"Key {namespaced_key!r} has no namespace separator {SEPARATOR!r}")
    namespace, _, key = namespaced_key.partition(SEPARATOR)
    return namespace, key


def list_namespaces(store) -> list[str]:
    """Return sorted unique namespaces present in the store."""
    namespaces: set[str] = set()
    for key in store.keys():
        if SEPARATOR in key:
            ns, _ = split_key(key)
            namespaces.add(ns)
    return sorted(namespaces)


def keys_in_namespace(store, namespace: str) -> list[str]:
    """Return all keys belonging to the given namespace."""
    prefix = f"{namespace.upper()}{SEPARATOR}"
    return sorted(k for k in store.keys() if k.startswith(prefix))


def get_namespace(store, namespace: str) -> dict[str, str]:
    """Return a dict of {short_key: value} for all keys in the namespace."""
    result: dict[str, str] = {}
    for full_key in keys_in_namespace(store, namespace):
        _, short_key = split_key(full_key)
        value = store.get(full_key)
        if value is not None:
            result[short_key] = value
    return result


def delete_namespace(store, namespace: str) -> int:
    """Remove all keys in the given namespace. Returns count of removed keys."""
    targets = keys_in_namespace(store, namespace)
    for key in targets:
        store.unset(key)
    return len(targets)
