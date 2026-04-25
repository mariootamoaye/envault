"""Clone (deep-copy) a vault or a subset of its keys into another profile."""

from __future__ import annotations

from typing import Iterable

from envault.store import VaultStore
from envault.profile import vault_path_for_profile


def clone_vault(
    src_store: VaultStore,
    dest_profile: str,
    password: str,
    *,
    keys: Iterable[str] | None = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Copy keys from *src_store* into the vault for *dest_profile*.

    Parameters
    ----------
    src_store:    Already-loaded source VaultStore.
    dest_profile: Name of the destination profile.
    password:     Master password used for the destination vault.
    keys:         Optional allowlist of keys to copy.  ``None`` copies all.
    overwrite:    When ``False`` (default) existing keys in the destination
                  are left untouched.

    Returns
    -------
    A mapping of ``{key: 'copied' | 'skipped'}`` for every candidate key.
    """
    dest_path = vault_path_for_profile(dest_profile)
    dest_store = VaultStore(dest_path, password)
    dest_store.load()

    candidate_keys = list(keys) if keys is not None else src_store.keys()

    report: dict[str, str] = {}
    for key in candidate_keys:
        value = src_store.get(key)
        if value is None:
            report[key] = "missing"
            continue
        if not overwrite and dest_store.get(key) is not None:
            report[key] = "skipped"
            continue
        dest_store.set(key, value)
        report[key] = "copied"

    dest_store.save()
    return report
