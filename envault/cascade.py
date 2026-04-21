"""Cascade: merge variables from multiple profiles with priority ordering."""

from __future__ import annotations

from typing import Dict, List, Tuple

from envault.store import VaultStore
from envault.profile import vault_path_for_profile


def _load_profile_data(profile: str, password: str) -> Dict[str, str]:
    """Load all key/value pairs from a single profile vault."""
    path = vault_path_for_profile(profile)
    store = VaultStore(path, password)
    return {k: store.get(k) for k in store.keys()}


def cascade(
    profiles: List[str],
    password: str,
) -> Dict[str, str]:
    """Merge variables from *profiles* in order; later profiles take priority.

    Args:
        profiles: Profile names ordered from lowest to highest priority.
        password: Shared vault password used for every profile.

    Returns:
        A plain dict with the merged key/value pairs.
    """
    merged: Dict[str, str] = {}
    for profile in profiles:
        data = _load_profile_data(profile, password)
        merged.update(data)
    return merged


def cascade_with_sources(
    profiles: List[str],
    password: str,
) -> Dict[str, Tuple[str, str]]:
    """Like :func:`cascade` but records which profile each key came from.

    Returns:
        Mapping of key -> (value, source_profile).
    """
    result: Dict[str, Tuple[str, str]] = {}
    for profile in profiles:
        data = _load_profile_data(profile, password)
        for k, v in data.items():
            result[k] = (v, profile)
    return result


def format_cascade(sourced: Dict[str, Tuple[str, str]]) -> str:
    """Render cascade_with_sources output as a human-readable table."""
    if not sourced:
        return "(no variables)"
    lines = []
    for key in sorted(sourced):
        value, source = sourced[key]
        lines.append(f"{key}={value!r}  [{source}]")
    return "\n".join(lines)
