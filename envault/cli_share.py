"""CLI commands for sharing vault secrets via encrypted bundles."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import _get_store, _prompt_password
from envault.share import export_bundle, import_bundle, save_bundle_file, load_bundle_file


@click.group("share")
def cmd_share() -> None:
    """Share secrets via encrypted bundle files."""


@cmd_share.command("export")
@click.argument("output", type=click.Path())
@click.option("--profile", default=None, help="Vault profile to use.")
@click.option("--share-password", default=None, help="Password for the bundle (defaults to vault password).")
def share_export(output: str, profile: str | None, share_password: str | None) -> None:
    """Export vault secrets to an encrypted bundle file."""
    password = _prompt_password()
    store = _get_store(password, profile)
    secrets = {k: store.get(k) for k in store.keys()}
    bundle_pw = share_password or password
    bundle = export_bundle(secrets, bundle_pw)
    save_bundle_file(bundle, Path(output))
    click.echo(f"Exported {len(secrets)} secret(s) to {output}.")


@cmd_share.command("import")
@click.argument("input", type=click.Path())
@click.option("--profile", default=None, help="Vault profile to use.")
@click.option("--share-password", default=None, help="Password used when the bundle was exported.")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist.")
def share_import(input: str, profile: str | None, share_password: str | None, no_overwrite: bool) -> None:
    """Import secrets from an encrypted bundle file into the vault."""
    try:
        bundle = load_bundle_file(Path(input))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    bundle_pw = share_password or click.prompt("Bundle password", hide_input=True)
    try:
        secrets = import_bundle(bundle, bundle_pw)
    except ValueError as exc:
        raise click.ClickException(f"Failed to decrypt bundle: {exc}")

    password = _prompt_password()
    store = _get_store(password, profile)
    imported = 0
    for key, value in secrets.items():
        if no_overwrite and store.get(key) is not None:
            continue
        store.set(key, value)
        imported += 1
    store.save()
    click.echo(f"Imported {imported} secret(s) from {input}.")
