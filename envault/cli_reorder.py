"""CLI commands for reordering vault keys."""

from __future__ import annotations

import click

from envault.cli import _get_store, _prompt_password
from envault.reorder import SORT_MODES, move_key, reorder_store


@click.group("reorder")
def cmd_reorder() -> None:
    """Reorder or sort vault keys."""


@cmd_reorder.command("sort")
@click.option(
    "--mode",
    default="alpha",
    show_default=True,
    type=click.Choice(SORT_MODES),
    help="Sort strategy.",
)
@click.option("--profile", default=None, help="Vault profile to use.")
def sort_cmd(mode: str, profile: str | None) -> None:
    """Sort all keys in the vault."""
    password = _prompt_password()
    store = _get_store(password, profile=profile)
    count = reorder_store(store, mode=mode)
    store.save()
    click.echo(f"Sorted {count} key(s) using mode '{mode}'.")


@cmd_reorder.command("move")
@click.argument("key")
@click.argument("position", type=int)
@click.option("--profile", default=None, help="Vault profile to use.")
def move_cmd(key: str, position: int, profile: str | None) -> None:
    """Move KEY to a specific POSITION (0-based index)."""
    password = _prompt_password()
    store = _get_store(password, profile=profile)
    raw = {k: store.get(k) for k in store.keys()}
    try:
        reordered = move_key(raw, key, position)
    except KeyError:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    for k in list(store.keys()):
        store.unset(k)
    for k, v in reordered.items():
        store.set(k, v)
    store.save()
    click.echo(f"Moved '{key}' to position {position}.")
