"""Secure vault sharing via encrypted export bundles."""

from __future__ import annotations

import json
import base64
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt


def export_bundle(secrets: Dict[str, str], password: str) -> str:
    """Encrypt a dict of secrets into a portable base64 bundle string."""
    payload = json.dumps(secrets)
    token = encrypt(payload, password)
    bundle = base64.urlsafe_b64encode(token.encode()).decode()
    return bundle


def import_bundle(bundle: str, password: str) -> Dict[str, str]:
    """Decrypt a bundle string back into a dict of secrets.

    Raises ValueError on bad password or corrupt bundle.
    """
    try:
        token = base64.urlsafe_b64decode(bundle.encode()).decode()
    except Exception as exc:
        raise ValueError("Invalid bundle format") from exc
    payload = decrypt(token, password)  # raises on bad password
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Bundle payload is not valid JSON") from exc


def save_bundle_file(bundle: str, path: Path) -> None:
    """Write a bundle string to a file."""
    path.write_text(bundle, encoding="utf-8")


def load_bundle_file(path: Path) -> str:
    """Read a bundle string from a file."""
    if not path.exists():
        raise FileNotFoundError(f"Bundle file not found: {path}")
    return path.read_text(encoding="utf-8").strip()
