"""CLI commands for scope management."""
from __future__ import annotations

from pathlib import Path

import click

from envault.scope import (
    keys_in_scope,
    list_scopes,
    load_scopes,
    remove_scope,
    set_scope,
)


@click.group(name="scope")
def cmd_scope() -> None:
    """Manage key scopes (e.g. prod, ci, local)."""


@cmd_scope.command(name="set")
@click.argument("key")
@click.argument("scope")
@click.option("--vault", default="vault.json", show_default=True)
def scope_set(key: str, scope: str, vault: str) -> None:
    """Assign KEY to SCOPE."""
    vault_path = Path(vault)
    try:
        set_scope(vault_path, key, scope)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Assigned {key!r} → scope {scope!r}")


@cmd_scope.command(name="unset")
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True)
def scope_unset(key: str, vault: str) -> None:
    """Remove scope assignment from KEY."""
    vault_path = Path(vault)
    removed = remove_scope(vault_path, key)
    if removed:
        click.echo(f"Removed scope from {key!r}")
    else:
        click.echo(f"{key!r} had no scope assigned")


@cmd_scope.command(name="list")
@click.option("--scope", default=None, help="Filter by scope name")
@click.option("--vault", default="vault.json", show_default=True)
def scope_list(scope: str | None, vault: str) -> None:
    """List keys and their scopes."""
    vault_path = Path(vault)
    if scope:
        keys = keys_in_scope(vault_path, scope)
        if not keys:
            click.echo(f"No keys in scope {scope!r}")
        else:
            for k in sorted(keys):
                click.echo(f"  {k}")
    else:
        scopes = load_scopes(vault_path)
        if not scopes:
            click.echo("No scopes defined")
        else:
            for k, s in sorted(scopes.items()):
                click.echo(f"  {k:<30} {s}")


@cmd_scope.command(name="scopes")
@click.option("--vault", default="vault.json", show_default=True)
def scope_names(vault: str) -> None:
    """List all distinct scope names."""
    vault_path = Path(vault)
    names = list_scopes(vault_path)
    if not names:
        click.echo("No scopes defined")
    else:
        for name in names:
            click.echo(name)
