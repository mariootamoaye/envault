"""Audit log for vault operations."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


DEFAULT_AUDIT_PATH = Path.home() / ".envault" / "audit.log"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(action: str, key: str | None = None, profile: str = "default", path: Path | None = None) -> None:
    """Append a single audit entry to the log file."""
    log_path = path or DEFAULT_AUDIT_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "action": action,
        "profile": profile,
    }
    if key is not None:
        entry["key"] = key
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read(path: Path | None = None) -> List[Dict[str, Any]]:
    """Return all audit entries as a list of dicts."""
    log_path = path or DEFAULT_AUDIT_PATH
    if not log_path.exists():
        return []
    entries = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def clear(path: Path | None = None) -> None:
    """Remove the audit log file."""
    log_path = path or DEFAULT_AUDIT_PATH
    if log_path.exists():
        log_path.unlink()
