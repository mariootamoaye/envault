"""Vault store: read/write encrypted .env vault files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from envault.crypto import decrypt, encrypt

DEFAULT_VAULT_PATH = Path(".envault")


class VaultStore:
    """Manages a local encrypted vault file."""

    def __init__(self, path: Path = DEFAULT_VAULT_PATH) -> None:
        self.path = path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, password: str) -> Dict[str, str]:
        """Load and decrypt all variables from the vault.

        Returns an empty dict when the vault file does not exist yet.
        """
        if not self.path.exists():
            return {}
        token = self.path.read_text(encoding="utf-8").strip()
        plaintext = decrypt(token, password)
        return json.loads(plaintext)

    def save(self, variables: Dict[str, str], password: str) -> None:
        """Encrypt *variables* and persist them to the vault file."""
        plaintext = json.dumps(variables)
        token = encrypt(plaintext, password)
        self.path.write_text(token, encoding="utf-8")

    def set(self, key: str, value: str, password: str) -> None:
        """Add or update a single variable in the vault."""
        variables = self.load(password)
        variables[key] = value
        self.save(variables, password)

    def unset(self, key: str, password: str) -> bool:
        """Remove a variable from the vault.  Returns True if it existed."""
        variables = self.load(password)
        existed = key in variables
        if existed:
            del variables[key]
            self.save(variables, password)
        return existed

    def list_keys(self, password: str) -> list[str]:
        """Return sorted list of stored variable names."""
        return sorted(self.load(password).keys())
