"""Value transformation rules for vault keys."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


TRANSFORM_OPS: Dict[str, Callable[[str, Optional[str]], str]] = {
    "upper": lambda v, _: v.upper(),
    "lower": lambda v, _: v.lower(),
    "strip": lambda v, _: v.strip(),
    "prefix": lambda v, arg: f"{arg}{v}" if arg else v,
    "suffix": lambda v, arg: f"{v}{arg}" if arg else v,
    "replace": lambda v, arg: v.replace(arg.split(":")[0], arg.split(":")[1]) if arg and ":" in arg else v,
}


class TransformError(ValueError):
    pass


def _transform_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".transforms.json")


def load_transforms(vault_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    p = _transform_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_transforms(vault_path: Path, data: Dict[str, List[Dict[str, Any]]]) -> None:
    p = _transform_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_transform(vault_path: Path, key: str, op: str, arg: Optional[str] = None) -> None:
    if not key:
        raise TransformError("key must not be empty")
    if op not in TRANSFORM_OPS:
        raise TransformError(f"unknown operation '{op}'; valid: {sorted(TRANSFORM_OPS)}")
    data = load_transforms(vault_path)
    data.setdefault(key, [])
    data[key].append({"op": op, "arg": arg})
    save_transforms(vault_path, data)


def remove_transforms(vault_path: Path, key: str) -> bool:
    data = load_transforms(vault_path)
    if key not in data:
        return False
    del data[key]
    save_transforms(vault_path, data)
    return True


def apply_transforms(vault_path: Path, key: str, value: str) -> str:
    data = load_transforms(vault_path)
    for step in data.get(key, []):
        op = step["op"]
        arg = step.get("arg")
        fn = TRANSFORM_OPS.get(op)
        if fn:
            value = fn(value, arg)
    return value


def apply_all(vault_path: Path, pairs: Dict[str, str]) -> Dict[str, str]:
    return {k: apply_transforms(vault_path, k, v) for k, v in pairs.items()}
