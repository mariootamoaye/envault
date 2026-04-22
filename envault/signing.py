"""Vault signing: generate and verify HMAC signatures for vault data."""

import hashlib
import hmac
import json
from pathlib import Path

_SIG_FILENAME = ".vault.sig"


def _sig_path(vault_path: Path) -> Path:
    """Return the path to the signature file alongside the vault."""
    return vault_path.parent / _SIG_FILENAME


def _canonical_bytes(data: dict) -> bytes:
    """Produce a deterministic byte representation of vault data."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def sign(data: dict, secret: str) -> str:
    """Return a hex HMAC-SHA256 signature of *data* using *secret*."""
    key = secret.encode()
    msg = _canonical_bytes(data)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify(data: dict, secret: str, signature: str) -> bool:
    """Return True if *signature* matches the HMAC of *data* with *secret*."""
    expected = sign(data, secret)
    return hmac.compare_digest(expected, signature)


def save_signature(vault_path: Path, data: dict, secret: str) -> None:
    """Compute and persist the signature for *data* next to *vault_path*."""
    sig = sign(data, secret)
    _sig_path(vault_path).write_text(sig)


def load_signature(vault_path: Path) -> str | None:
    """Load the stored signature, or None if it does not exist."""
    path = _sig_path(vault_path)
    if not path.exists():
        return None
    return path.read_text().strip()


def verify_vault(vault_path: Path, data: dict, secret: str) -> bool:
    """Return True if the stored signature matches *data*.

    Returns False when no signature file exists.
    """
    stored = load_signature(vault_path)
    if stored is None:
        return False
    return verify(data, secret, stored)


def clear_signature(vault_path: Path) -> None:
    """Remove the signature file if it exists."""
    path = _sig_path(vault_path)
    if path.exists():
        path.unlink()
