"""Tests for envault.schedule."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from envault.schedule import (
    set_schedule,
    remove_schedule,
    get_schedule,
    load_schedules,
    due_keys,
    _compute_next_due,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_schedules(vault_path) == {}


def test_set_schedule_creates_entry(vault_path):
    entry = set_schedule(vault_path, "API_KEY", 30, "days")
    assert entry["interval"] == 30
    assert entry["unit"] == "days"
    assert "next_due" in entry
    assert "created_at" in entry


def test_set_schedule_persists(vault_path):
    set_schedule(vault_path, "DB_PASS", 2, "weeks")
    schedules = load_schedules(vault_path)
    assert "DB_PASS" in schedules
    assert schedules["DB_PASS"]["interval"] == 2


def test_set_schedule_overwrites_existing(vault_path):
    set_schedule(vault_path, "TOKEN", 7, "days")
    set_schedule(vault_path, "TOKEN", 1, "months")
    entry = get_schedule(vault_path, "TOKEN")
    assert entry["interval"] == 1
    assert entry["unit"] == "months"


def test_set_schedule_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="empty"):
        set_schedule(vault_path, "", 7, "days")


def test_set_schedule_invalid_unit_raises(vault_path):
    with pytest.raises(ValueError, match="unit"):
        set_schedule(vault_path, "KEY", 5, "hours")


def test_set_schedule_non_positive_interval_raises(vault_path):
    with pytest.raises(ValueError, match="positive"):
        set_schedule(vault_path, "KEY", 0, "days")


def test_remove_schedule_returns_true_when_exists(vault_path):
    set_schedule(vault_path, "MY_KEY", 14, "days")
    assert remove_schedule(vault_path, "MY_KEY") is True
    assert get_schedule(vault_path, "MY_KEY") is None


def test_remove_schedule_returns_false_when_missing(vault_path):
    assert remove_schedule(vault_path, "GHOST") is False


def test_due_keys_returns_overdue_entries(vault_path):
    set_schedule(vault_path, "OLD_KEY", 1, "days")
    # Manually backdate next_due
    import json
    from envault.schedule import _schedule_path
    data = json.loads(_schedule_path(vault_path).read_text())
    data["OLD_KEY"]["next_due"] = (datetime.utcnow() - timedelta(days=1)).isoformat()
    _schedule_path(vault_path).write_text(json.dumps(data))

    result = due_keys(vault_path)
    assert "OLD_KEY" in result


def test_due_keys_excludes_future_entries(vault_path):
    set_schedule(vault_path, "FRESH_KEY", 90, "days")
    result = due_keys(vault_path)
    assert "FRESH_KEY" not in result


def test_compute_next_due_days():
    base = datetime(2024, 1, 1)
    result = _compute_next_due(base, 10, "days")
    assert result == datetime(2024, 1, 11)


def test_compute_next_due_weeks():
    base = datetime(2024, 1, 1)
    result = _compute_next_due(base, 2, "weeks")
    assert result == datetime(2024, 1, 15)


def test_compute_next_due_months():
    base = datetime(2024, 1, 1)
    result = _compute_next_due(base, 1, "months")
    assert result == datetime(2024, 1, 31)
