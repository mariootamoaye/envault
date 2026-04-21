"""CLI commands for managing key expiry dates."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from envault.cli import _get_store, _prompt_password
from envault.expiry import (
    expired_keys,
    get_expiry,
    purge_expired,
    remove_expiry,
    set_expiry,
)

_DATE_FMT = "%Y-%m-%d"
_DATETIME_FMT = "%Y-%m-%dT%H:%M"


def _parse_date(value: str) -> datetime:
    for fmt in (_DATETIME_FMT, _DATE_FMT):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise click.BadParameter(
        f"Expected YYYY-MM-DD or YYYY-MM-DDTHH:MM, got '{value}'"
    )


@click.group(name="expiry")
def cmd_expiry():
    """Manage key expiry dates."""


@cmd_expiry.command("set")
@click.argument("key")
@click.argument("date")
@click.option("--vault", default=".envault", show_default=True)
def expiry_set(key: str, date: str, vault: str):
    """Set an expiry DATE (YYYY-MM-DD) on KEY."""
    vault_path = Path(vault)
    expires_at = _parse_date(date)
    set_expiry(vault_path, key, expires_at)
    click.echo(f"Expiry for '{key}' set to {expires_at.date().isoformat()}.")


@cmd_expiry.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def expiry_get(key: str, vault: str):
    """Show the expiry date for KEY."""
    vault_path = Path(vault)
    exp = get_expiry(vault_path, key)
    if exp is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        click.echo(exp.date().isoformat())


@cmd_expiry.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def expiry_remove(key: str, vault: str):
    """Remove the expiry date from KEY."""
    vault_path = Path(vault)
    remove_expiry(vault_path, key)
    click.echo(f"Expiry removed for '{key}'.")


@cmd_expiry.command("list")
@click.option("--vault", default=".envault", show_default=True)
def expiry_list(vault: str):
    """List all expired keys."""
    vault_path = Path(vault)
    keys = expired_keys(vault_path)
    if not keys:
        click.echo("No expired keys.")
    else:
        for k in keys:
            click.echo(k)


@cmd_expiry.command("purge")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", default=None, help="Vault password.")
def expiry_purge(vault: str, password: str):
    """Delete all expired keys from the vault."""
    vault_path = Path(vault)
    if password is None:
        password = _prompt_password()
    store = _get_store(vault_path, password)
    purged = purge_expired(vault_path, store)
    if not purged:
        click.echo("Nothing to purge.")
    else:
        store.save()
        click.echo(f"Purged {len(purged)} key(s): {', '.join(purged)}")
