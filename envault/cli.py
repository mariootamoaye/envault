"""envault CLI entry-point."""

from __future__ import annotations

import os
from pathlib import Path

import click

from envault.store import VaultStore

VAULT_PATH_ENV = "ENVAULT_PATH"


def _get_store() -> VaultStore:
    path = Path(os.environ.get(VAULT_PATH_ENV, ".envault"))
    return VaultStore(path=path)


def _prompt_password() -> str:
    return click.prompt("Vault password", hide_input=True)


@click.group()
def cli() -> None:
    """envault — secure environment variable manager."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
def cmd_set(key: str, value: str) -> None:
    """Store KEY=VALUE in the vault."""
    password = _prompt_password()
    _get_store().set(key, value, password)
    click.echo(f"✔  {key} stored.")


@cli.command("unset")
@click.argument("key")
def cmd_unset(key: str) -> None:
    """Remove KEY from the vault."""
    password = _prompt_password()
    removed = _get_store().unset(key, password)
    if removed:
        click.echo(f"✔  {key} removed.")
    else:
        click.echo(f"⚠  {key} not found.", err=True)


@cli.command("list")
def cmd_list() -> None:
    """List all stored variable names."""
    password = _prompt_password()
    keys = _get_store().list_keys(password)
    if keys:
        click.echo("\n".join(keys))
    else:
        click.echo("(vault is empty)")


@cli.command("export")
def cmd_export() -> None:
    """Print variables as export statements for eval."""
    password = _prompt_password()
    variables = _get_store().load(password)
    for key, value in sorted(variables.items()):
        click.echo(f"export {key}={value!r}")
