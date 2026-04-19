"""CLI commands for profile management."""
from __future__ import annotations

import click

from envault.profile import list_profiles, get_profile_name
from envault.cli import _get_store, _prompt_password


@click.group("profile")
def cmd_profile():
    """Manage named vault profiles."""


@cmd_profile.command("list")
@click.option("--dir", "base_dir", default=None, hidden=True)
def profile_list(base_dir):
    """List all available profiles."""
    from pathlib import Path
    from envault.store import VaultStore

    bd = Path(base_dir) if base_dir else VaultStore._default_dir()
    profiles = list_profiles(bd)
    if not profiles:
        click.echo("No profiles found.")
        return
    active = get_profile_name()
    for name in profiles:
        marker = " (active)" if name == active else ""
        click.echo(f"  {name}{marker}")


@cmd_profile.command("copy")
@click.argument("src_profile")
@click.argument("dst_profile")
def profile_copy(src_profile, dst_profile):
    """Copy all variables from SRC_PROFILE to DST_PROFILE."""
    password = _prompt_password()
    src_store = _get_store(password, profile=src_profile)
    dst_store = _get_store(password, profile=dst_profile)
    items = src_store.all()
    if not items:
        click.echo(f"Profile '{src_profile}' is empty.")
        return
    for key, value in items.items():
        dst_store.set(key, value)
    dst_store.save(password)
    click.echo(f"Copied {len(items)} variable(s) from '{src_profile}' to '{dst_profile}'.")
