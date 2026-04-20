"""CLI commands for managing key rotation reminders."""
from __future__ import annotations

from pathlib import Path

import click

from envault.remind import get_due, list_reminders, remove_reminder, set_reminder


@click.group(name="remind")
def cmd_remind() -> None:
    """Manage rotation reminders for vault keys."""


@cmd_remind.command(name="set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def remind_set(key: str, days: int, vault_dir: str) -> None:
    """Set a reminder for KEY in DAYS days."""
    try:
        due = set_reminder(Path(vault_dir), key, days)
        click.echo(f"Reminder set for '{key}' — due {due.isoformat()}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_remind.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def remind_remove(key: str, vault_dir: str) -> None:
    """Remove the reminder for KEY."""
    removed = remove_reminder(Path(vault_dir), key)
    if removed:
        click.echo(f"Reminder for '{key}' removed.")
    else:
        click.echo(f"No reminder found for '{key}'.")


@cmd_remind.command(name="list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--due", is_flag=True, default=False, help="Show only overdue reminders.")
def remind_list(vault_dir: str, due: bool) -> None:
    """List reminders, optionally filtering to overdue ones."""
    path = Path(vault_dir)
    entries = get_due(path) if due else list_reminders(path)
    if not entries:
        click.echo("No reminders." if not due else "No overdue reminders.")
        return
    for entry in entries:
        click.echo(f"{entry['key']:30s}  due {entry['due']}")
