"""Reminders: flag vault keys for periodic rotation review."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

_REMIND_FILE = ".envault_reminders.json"


def _remind_path(vault_dir: Path) -> Path:
    return vault_dir / _REMIND_FILE


def load_reminders(vault_dir: Path) -> dict:
    path = _remind_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_reminders(vault_dir: Path, data: dict) -> None:
    _remind_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_reminder(vault_dir: Path, key: str, days: int) -> date:
    """Schedule a reminder for *key* in *days* days. Returns the due date."""
    if days < 1:
        raise ValueError("days must be a positive integer")
    due = date.today() + timedelta(days=days)
    reminders = load_reminders(vault_dir)
    reminders[key] = due.isoformat()
    save_reminders(vault_dir, reminders)
    return due


def remove_reminder(vault_dir: Path, key: str) -> bool:
    """Remove reminder for *key*. Returns True if it existed."""
    reminders = load_reminders(vault_dir)
    if key not in reminders:
        return False
    del reminders[key]
    save_reminders(vault_dir, reminders)
    return True


def get_due(vault_dir: Path, today: Optional[date] = None) -> list[dict]:
    """Return list of reminder dicts whose due date <= today."""
    today = today or date.today()
    reminders = load_reminders(vault_dir)
    due = []
    for key, iso in reminders.items():
        if date.fromisoformat(iso) <= today:
            due.append({"key": key, "due": iso})
    due.sort(key=lambda d: d["due"])
    return due


def list_reminders(vault_dir: Path) -> list[dict]:
    """Return all reminders sorted by due date."""
    reminders = load_reminders(vault_dir)
    result = [{"key": k, "due": v} for k, v in reminders.items()]
    result.sort(key=lambda d: d["due"])
    return result
