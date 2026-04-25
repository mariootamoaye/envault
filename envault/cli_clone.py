"""CLI command: envault clone — copy keys from one profile to another."""

from __future__ import annotations

import click

from envault.cli import _get_store, _prompt_password
from envault.clone import clone_vault


@click.group("clone")
def cmd_clone() -> None:
    """Clone keys between profiles."""


@cmd_clone.command("run")
@click.argument("dest_profile")
@click.option("--profile", default="default", show_default=True, help="Source profile.")
@click.option("--keys", default=None, help="Comma-separated list of keys to copy.")
@click.option(
    "--overwrite", is_flag=True, default=False, help="Overwrite existing keys in dest."
)
def clone_run(
    dest_profile: str,
    profile: str,
    keys: str | None,
    overwrite: bool,
) -> None:
    """Copy keys from SOURCE profile into DEST_PROFILE."""
    if dest_profile == profile:
        raise click.UsageError("Source and destination profiles must differ.")

    password = _prompt_password()
    src_store = _get_store(profile, password)

    key_list = [k.strip() for k in keys.split(",")] if keys else None

    report = clone_vault(
        src_store,
        dest_profile,
        password,
        keys=key_list,
        overwrite=overwrite,
    )

    copied = [k for k, s in report.items() if s == "copied"]
    skipped = [k for k, s in report.items() if s == "skipped"]
    missing = [k for k, s in report.items() if s == "missing"]

    if copied:
        click.echo(f"Copied  ({len(copied)}): {', '.join(copied)}")
    if skipped:
        click.echo(f"Skipped ({len(skipped)}): {', '.join(skipped)}")
    if missing:
        click.echo(f"Missing ({len(missing)}): {', '.join(missing)}")
    if not report:
        click.echo("Nothing to clone.")
