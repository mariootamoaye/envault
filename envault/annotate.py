"""Key annotation support — attach freeform notes/comments to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


def _annotate_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".annotations.json")


def load_annotations(vault_path: Path) -> Dict[str, str]:
    """Return {key: note} mapping; empty dict if file absent."""
    p = _annotate_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_annotations(vault_path: Path, annotations: Dict[str, str]) -> None:
    p = _annotate_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(annotations, indent=2))


def set_annotation(vault_path: Path, key: str, note: str) -> None:
    """Attach *note* to *key*, overwriting any previous annotation."""
    if not key:
        raise ValueError("key must not be empty")
    annotations = load_annotations(vault_path)
    annotations[key] = note
    save_annotations(vault_path, annotations)


def remove_annotation(vault_path: Path, key: str) -> bool:
    """Remove annotation for *key*. Returns True if it existed."""
    annotations = load_annotations(vault_path)
    if key not in annotations:
        return False
    del annotations[key]
    save_annotations(vault_path, annotations)
    return True


def get_annotation(vault_path: Path, key: str) -> Optional[str]:
    """Return the note for *key*, or None."""
    return load_annotations(vault_path).get(key)


def list_annotations(vault_path: Path) -> Dict[str, str]:
    """Return all {key: note} pairs."""
    return load_annotations(vault_path)
