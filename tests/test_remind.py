"""Tests for envault.remind."""
from datetime import date, timedelta
from pathlib import Path

import pytest

from envault.remind import (
    get_due,
    list_reminders,
    load_reminders,
    remove_reminder,
    set_reminder,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_returns_empty_when_no_file(vault_dir):
    assert load_reminders(vault_dir) == {}


def test_set_reminder_creates_entry(vault_dir):
    due = set_reminder(vault_dir, "API_KEY", 30)
    assert due == date.today() + timedelta(days=30)
    reminders = load_reminders(vault_dir)
    assert "API_KEY" in reminders
    assert reminders["API_KEY"] == due.isoformat()


def test_set_reminder_overwrites_existing(vault_dir):
    set_reminder(vault_dir, "API_KEY", 10)
    set_reminder(vault_dir, "API_KEY", 60)
    reminders = load_reminders(vault_dir)
    expected = (date.today() + timedelta(days=60)).isoformat()
    assert reminders["API_KEY"] == expected


def test_set_reminder_invalid_days_raises(vault_dir):
    with pytest.raises(ValueError):
        set_reminder(vault_dir, "API_KEY", 0)


def test_remove_reminder_returns_true_when_exists(vault_dir):
    set_reminder(vault_dir, "SECRET", 7)
    assert remove_reminder(vault_dir, "SECRET") is True
    assert "SECRET" not in load_reminders(vault_dir)


def test_remove_reminder_returns_false_when_missing(vault_dir):
    assert remove_reminder(vault_dir, "GHOST") is False


def test_get_due_returns_overdue_entries(vault_dir):
    past = date.today() - timedelta(days=1)
    future = date.today() + timedelta(days=5)
    reminders = {"OLD_KEY": past.isoformat(), "NEW_KEY": future.isoformat()}
    from envault.remind import save_reminders
    save_reminders(vault_dir, reminders)
    due = get_due(vault_dir)
    assert len(due) == 1
    assert due[0]["key"] == "OLD_KEY"


def test_get_due_includes_today(vault_dir):
    today = date.today()
    from envault.remind import save_reminders
    save_reminders(vault_dir, {"TODAY_KEY": today.isoformat()})
    due = get_due(vault_dir)
    assert any(d["key"] == "TODAY_KEY" for d in due)


def test_list_reminders_sorted_by_date(vault_dir):
    set_reminder(vault_dir, "B_KEY", 20)
    set_reminder(vault_dir, "A_KEY", 5)
    result = list_reminders(vault_dir)
    assert result[0]["key"] == "A_KEY"
    assert result[1]["key"] == "B_KEY"
