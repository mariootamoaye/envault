"""Redaction rules: mark keys whose values should never appear in logs or output."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

_DEFAULT_PATTERNS: List[str] = [
    r"(?i)(password|passwd|secret|token|key|api_?key|auth|credential|private)",
]


def _redact_path(vault_path: Path) -> Path:
    return vault_path.parent / "redact.json"


def load_redact(vault_path: Path) -> Dict[str, object]:
    """Return persisted redact config: {patterns: [...], keys: [...]}"""
    p = _redact_path(vault_path)
    if not p.exists():
        return {"patterns": list(_DEFAULT_PATTERNS), "keys": []}
    with p.open() as fh:
        return json.load(fh)


def save_redact(vault_path: Path, config: Dict[str, object]) -> None:
    p = _redact_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as fh:
        json.dump(config, fh, indent=2)


def pin_key(vault_path: Path, key: str) -> None:
    """Explicitly mark *key* as redacted regardless of pattern matching."""
    cfg = load_redact(vault_path)
    keys: List[str] = cfg.setdefault("keys", [])
    if key not in keys:
        keys.append(key)
    save_redact(vault_path, cfg)


def unpin_key(vault_path: Path, key: str) -> None:
    """Remove explicit redaction mark from *key*."""
    cfg = load_redact(vault_path)
    cfg["keys"] = [k for k in cfg.get("keys", []) if k != key]
    save_redact(vault_path, cfg)


def add_pattern(vault_path: Path, pattern: str) -> None:
    """Add a regex pattern that auto-marks matching key names as redacted."""
    re.compile(pattern)  # validate early
    cfg = load_redact(vault_path)
    patterns: List[str] = cfg.setdefault("patterns", [])
    if pattern not in patterns:
        patterns.append(pattern)
    save_redact(vault_path, cfg)


def is_redacted(vault_path: Path, key: str) -> bool:
    """Return True if *key* should be treated as redacted."""
    cfg = load_redact(vault_path)
    if key in cfg.get("keys", []):
        return True
    for pat in cfg.get("patterns", []):
        if re.search(pat, key):
            return True
    return False


def redact_dict(
    vault_path: Path,
    data: Dict[str, str],
    placeholder: str = "**REDACTED**",
) -> Dict[str, str]:
    """Return a copy of *data* with redacted values replaced by *placeholder*."""
    return {
        k: (placeholder if is_redacted(vault_path, k) else v)
        for k, v in data.items()
    }
