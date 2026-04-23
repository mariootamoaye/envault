"""CLI sub-commands for managing event notifications."""

from __future__ import annotations

import click

from envault.notify import add_notify, fire, load_notify, remove_notify
from envault.profile import vault_path_for_profile, get_profile_name


@click.group(name="notify")
@click.pass_context
def cmd_notify(ctx: click.Context) -> None:
    """Manage event-triggered notifications."""
    ctx.ensure_object(dict)
    profile = get_profile_name(ctx.obj.get("profile"))
    ctx.obj["vault_path"] = vault_path_for_profile(profile)


@cmd_notify.command(name="add")
@click.argument("event")
@click.argument("command")
@click.pass_context
def notify_add(ctx: click.Context, event: str, command: str) -> None:
    """Register COMMAND to run when EVENT fires."""
    vault_path = ctx.obj["vault_path"]
    try:
        add_notify(vault_path, event, command)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Registered '{command}' for event '{event}'.")


@cmd_notify.command(name="remove")
@click.argument("event")
@click.argument("command")
@click.pass_context
def notify_remove(ctx: click.Context, event: str, command: str) -> None:
    """Remove COMMAND from EVENT."""
    vault_path = ctx.obj["vault_path"]
    removed = remove_notify(vault_path, event, command)
    if removed:
        click.echo(f"Removed '{command}' from event '{event}'.")
    else:
        click.echo(f"Command not found for event '{event}'.")


@cmd_notify.command(name="list")
@click.pass_context
def notify_list(ctx: click.Context) -> None:
    """List all registered notifications."""
    vault_path = ctx.obj["vault_path"]
    config = load_notify(vault_path)
    if not config:
        click.echo("No notifications configured.")
        return
    for event, commands in sorted(config.items()):
        for cmd in commands:
            click.echo(f"{event}: {cmd}")


@cmd_notify.command(name="fire")
@click.argument("event")
@click.pass_context
def notify_fire(ctx: click.Context, event: str) -> None:
    """Manually fire EVENT and run its registered commands."""
    vault_path = ctx.obj["vault_path"]
    results = fire(vault_path, event)
    if not results:
        click.echo(f"No commands registered for event '{event}'.")
    else:
        for i, rc in enumerate(results, 1):
            status = "ok" if rc == 0 else f"exit {rc}"
            click.echo(f"  command {i}: {status}")
