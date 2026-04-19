"""CLI commands for importing environment variables into the vault."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envault.cli import _get_store, _prompt_password
from envault.import_env import import_from_file, import_from_env


@click.group()
def cmd_import() -> None:
    """Import variables into the vault."""


@cmd_import.command("file")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
def import_file(
    env_file: Path,
    vault_path: str,
    overwrite: bool,
) -> None:
    """Import variables from a .env FILE into the vault."""
    password = _prompt_password(confirm=False)
    store = _get_store(vault_path, password)
    pairs = import_from_file(env_file)
    skipped = 0
    imported = 0
    for key, value in pairs.items():
        if not overwrite and store.get(key) is not None:
            skipped += 1
            continue
        store.set(key, value)
        imported += 1
    store.save(password)
    click.echo(f"Imported {imported} variable(s), skipped {skipped}.")


@cmd_import.command("env")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--overwrite/--no-overwrite", default=False, show_default=True)
def import_env_cmd(
    keys: tuple[str, ...],
    vault_path: str,
    overwrite: bool,
) -> None:
    """Import specific KEYS from the current environment into the vault."""
    password = _prompt_password(confirm=False)
    store = _get_store(vault_path, password)
    pairs = import_from_env(keys=list(keys))
    imported = 0
    for key, value in pairs.items():
        if not overwrite and store.get(key) is not None:
            continue
        store.set(key, value)
        imported += 1
    store.save(password)
    click.echo(f"Imported {imported} variable(s) from environment.")
