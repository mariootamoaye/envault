"""CLI command for password rotation."""

from __future__ import annotations

import click

from envault.cli import _get_store, _prompt_password
from envault.profile import vault_path_for_profile
from envault.rotate import rotate_password


@click.command("rotate")
@click.option("--profile", default=None, help="Vault profile to rotate.")
@click.pass_context
def cmd_rotate(ctx: click.Context, profile: str | None) -> None:
    """Re-encrypt the vault with a new master password."""
    vault_path = vault_path_for_profile(profile)

    click.echo("Enter the CURRENT master password:")
    old_password = _prompt_password(confirm=False)

    # Verify old password by attempting a load
    try:
        store = _get_store(vault_path, old_password)
        store.load()
    except Exception:
        raise click.ClickException("Current password is incorrect or vault is corrupt.")

    click.echo("Enter the NEW master password:")
    new_password = _prompt_password(confirm=True)

    if old_password == new_password:
        raise click.ClickException("New password must differ from the current password.")

    count = rotate_password(vault_path, old_password, new_password)
    click.echo(f"Rotated {count} secret(s) successfully.")
