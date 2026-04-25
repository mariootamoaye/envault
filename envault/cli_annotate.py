"""CLI commands for managing key annotations."""

from __future__ import annotations

import click
from pathlib import Path

from envault.annotate import (
    set_annotation,
    remove_annotation,
    get_annotation,
    list_annotations,
)


@click.group("annotate")
def cmd_annotate():
    """Attach notes/comments to vault keys."""


@cmd_annotate.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def annotate_set(key: str, note: str, vault_path: str):
    """Attach NOTE to KEY."""
    try:
        set_annotation(Path(vault_path), key, note)
        click.echo(f"Annotation set for '{key}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_annotate.command("remove")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def annotate_remove(key: str, vault_path: str):
    """Remove annotation from KEY."""
    removed = remove_annotation(Path(vault_path), key)
    if removed:
        click.echo(f"Annotation removed for '{key}'.")
    else:
        click.echo(f"No annotation found for '{key}'.")


@cmd_annotate.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def annotate_get(key: str, vault_path: str):
    """Show annotation for KEY."""
    note = get_annotation(Path(vault_path), key)
    if note is None:
        click.echo(f"No annotation for '{key}'.")
    else:
        click.echo(note)


@cmd_annotate.command("list")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def annotate_list(vault_path: str):
    """List all annotated keys."""
    annotations = list_annotations(Path(vault_path))
    if not annotations:
        click.echo("No annotations.")
        return
    for key, note in sorted(annotations.items()):
        click.echo(f"{key}: {note}")
