"""Schedule-based auto-refresh reminders for vault keys."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

_VALID_UNITS = {"days", "weeks", "months"}


def _schedule_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".schedule.json")


def _now() -> datetime:
    return datetime.utcnow()


def load_schedules(vault_path: Path) -> Dict[str, dict]:
    """Load all scheduled refresh entries for a vault."""
    path = _schedule_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_schedules(vault_path: Path, data: Dict[str, dict]) -> None:
    path = _schedule_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_schedule(vault_path: Path, key: str, interval: int, unit: str) -> dict:
    """Set a refresh schedule for a key. unit must be days/weeks/months."""
    if not key:
        raise ValueError("key must not be empty")
    if unit not in _VALID_UNITS:
        raise ValueError(f"unit must be one of {sorted(_VALID_UNITS)}")
    if interval <= 0:
        raise ValueError("interval must be a positive integer")

    schedules = load_schedules(vault_path)
    entry = {
        "interval": interval,
        "unit": unit,
        "created_at": _now().isoformat(),
        "next_due": _compute_next_due(_now(), interval, unit).isoformat(),
    }
    schedules[key] = entry
    save_schedules(vault_path, schedules)
    return entry


def remove_schedule(vault_path: Path, key: str) -> bool:
    """Remove the schedule for a key. Returns True if it existed."""
    schedules = load_schedules(vault_path)
    if key not in schedules:
        return False
    del schedules[key]
    save_schedules(vault_path, schedules)
    return True


def get_schedule(vault_path: Path, key: str) -> Optional[dict]:
    return load_schedules(vault_path).get(key)


def due_keys(vault_path: Path, as_of: Optional[datetime] = None) -> List[str]:
    """Return keys whose refresh is due on or before *as_of* (default: now)."""
    now = as_of or _now()
    schedules = load_schedules(vault_path)
    return [
        k for k, v in schedules.items()
        if datetime.fromisoformat(v["next_due"]) <= now
    ]


def _compute_next_due(from_dt: datetime, interval: int, unit: str) -> datetime:
    if unit == "days":
        return from_dt + timedelta(days=interval)
    if unit == "weeks":
        return from_dt + timedelta(weeks=interval)
    # months: approximate as 30 days each
    return from_dt + timedelta(days=interval * 30)
