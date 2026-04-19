"""Key rotation: re-encrypt vault contents with a new password."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from envault.store import VaultStore


def rotate_password(
    vault_path: "Path",
    old_password: str,
    new_password: str,
) -> int:
    """Re-encrypt all secrets in *vault_path* under *new_password*.

    Returns the number of keys that were rotated.
    Raises ``ValueError`` / ``cryptography`` exceptions if *old_password* is wrong.
    """
    store = VaultStore(vault_path, old_password)
    store.load()

    keys = store.list()
    values = {k: store.get(k) for k in keys}

    # Overwrite with new password
    new_store = VaultStore(vault_path, new_password)
    # Start fresh so we don't mix ciphertexts
    new_store._data = {}
    for k, v in values.items():
        new_store.set(k, v)
    new_store.save()

    return len(keys)
