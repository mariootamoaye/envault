"""CLI commands for managing key refresh schedules."""

from __future__ import annotations

import click
from pathlib import Path

from envault.schedule import (
    set_schedule,
    remove_schedule,
    get_schedule,
    load_schedules,
    due_keys,
)


@click.group(name="schedule")
def cmd_schedule():
    """Manage key refresh schedules."""


@cmd_schedule.command(name="set")
@click.argument("key")
@click.option("--every", required=True, type=int, help="Interval amount.")
@click.option(
    "--unit",
    default="days",
    show_default=True,
    type=click.Choice(["days", "weeks", "months"]),
    help="Interval unit.",
)
@click.pass_context
def schedule_set(ctx: click.Context, key: str, every: int, unit: str):
    """Set a refresh schedule for KEY."""
    vault_path = Path(ctx.obj["vault_path"])
    try:
        entry = set_schedule(vault_path, key, every, unit)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Scheduled '{key}' every {every} {unit}. Next due: {entry['next_due']}")


@cmd_schedule.command(name="remove")
@click.argument("key")
@click.pass_context
def schedule_remove(ctx: click.Context, key: str):
    """Remove the refresh schedule for KEY."""
    vault_path = Path(ctx.obj["vault_path"])
    removed = remove_schedule(vault_path, key)
    if removed:
        click.echo(f"Schedule for '{key}' removed.")
    else:
        click.echo(f"No schedule found for '{key}'.")


@cmd_schedule.command(name="list")
@click.pass_context
def schedule_list(ctx: click.Context):
    """List all scheduled keys."""
    vault_path = Path(ctx.obj["vault_path"])
    schedules = load_schedules(vault_path)
    if not schedules:
        click.echo("No schedules configured.")
        return
    for key, info in sorted(schedules.items()):
        click.echo(f"{key}: every {info['interval']} {info['unit']}, next due {info['next_due']}")


@cmd_schedule.command(name="due")
@click.pass_context
def schedule_due(ctx: click.Context):
    """Show keys whose refresh is currently due."""
    vault_path = Path(ctx.obj["vault_path"])
    keys = due_keys(vault_path)
    if not keys:
        click.echo("No keys are due for refresh.")
        return
    click.echo("Keys due for refresh:")
    for key in sorted(keys):
        click.echo(f"  {key}")
