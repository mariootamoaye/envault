"""CLI commands for archiving (soft-deleting) vault keys."""

from __future__ import annotations

import click

from envault.cli import _get_store, _prompt_password
from envault.archive import (
    archive_key,
    restore_key,
    list_archived,
    purge_archive,
)


@click.group(name="archive")
def cmd_archive() -> None:
    """Soft-delete, restore, or purge archived keys."""


@cmd_archive.command("add")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def archive_add(key: str, profile: str) -> None:
    """Archive KEY (remove from live vault, keep recoverable)."""
    password = _prompt_password()
    store, vault_path = _get_store(profile, password)
    if archive_key(vault_path, store, key):
        click.echo(f"Archived '{key}'.")
    else:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)


@cmd_archive.command("restore")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def archive_restore(key: str, profile: str) -> None:
    """Restore KEY from the archive back into the live vault."""
    password = _prompt_password()
    store, vault_path = _get_store(profile, password)
    if restore_key(vault_path, store, key):
        click.echo(f"Restored '{key}' to vault.")
    else:
        click.echo(f"Key '{key}' not found in archive.", err=True)
        raise SystemExit(1)


@cmd_archive.command("list")
@click.option("--profile", default="default", show_default=True)
def archive_list(profile: str) -> None:
    """List all archived keys."""
    password = _prompt_password()
    _store, vault_path = _get_store(profile, password)
    keys = list_archived(vault_path)
    if not keys:
        click.echo("No archived keys.")
    else:
        for k in keys:
            click.echo(k)


@cmd_archive.command("purge")
@click.argument("key", required=False, default=None)
@click.option("--profile", default="default", show_default=True)
@click.confirmation_option(prompt="Permanently delete archived key(s)?")
def archive_purge(key: str | None, profile: str) -> None:
    """Permanently delete KEY from archive (or all keys if KEY omitted)."""
    password = _prompt_password()
    _store, vault_path = _get_store(profile, password)
    count = purge_archive(vault_path, key)
    click.echo(f"Purged {count} archived key(s).")
