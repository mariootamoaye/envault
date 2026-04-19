"""Search/filter vault keys by pattern."""
from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envault.store import VaultStore


def search_keys(
    store: VaultStore,
    password: str,
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return vault entries whose keys match *pattern* (glob-style).

    Args:
        store: An open VaultStore instance.
        password: Master password used to decrypt values.
        pattern: Glob pattern, e.g. ``DB_*`` or ``*SECRET*``.
        case_sensitive: When False (default) matching ignores case.

    Returns:
        Mapping of matching key -> decrypted value.
    """
    all_keys: List[str] = store.list()
    results: Dict[str, str] = {}

    for key in all_keys:
        target = key if case_sensitive else key.upper()
        pat = pattern if case_sensitive else pattern.upper()
        if fnmatch.fnmatchcase(target, pat):
            value = store.get(key, password)
            if value is not None:
                results[key] = value

    return results


def search_values(
    store: VaultStore,
    password: str,
    substring: str,
    *,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return vault entries whose decrypted values contain *substring*.

    Args:
        store: An open VaultStore instance.
        password: Master password used to decrypt values.
        substring: String to look for inside values.
        case_sensitive: When False (default) matching ignores case.

    Returns:
        Mapping of matching key -> decrypted value.
    """
    all_keys: List[str] = store.list()
    results: Dict[str, str] = {}

    needle = substring if case_sensitive else substring.lower()

    for key in all_keys:
        value = store.get(key, password)
        if value is None:
            continue
        haystack = value if case_sensitive else value.lower()
        if needle in haystack:
            results[key] = value

    return results
