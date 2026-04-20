"""CLI commands for vault backup and restore."""

import click
from pathlib import Path

from envault.backup import backup_vault, restore_vault, list_backups, delete_backup
from envault.cli import _get_store
from envault.profile import vault_path_for_profile, get_profile_name


@click.group(name="backup")
def cmd_backup():
    """Backup and restore vault data."""


@cmd_backup.command(name="create")
@click.option("--profile", default=None, help="Profile name.")
@click.option(
    "--backup-dir",
    default=None,
    help="Directory to store backups (default: ~/.envault/backups).",
)
def backup_create(profile, backup_dir):
    """Create a compressed backup of the current vault."""
    profile_name = get_profile_name(override=profile)
    vault_path = vault_path_for_profile(profile_name)
    bdir = Path(backup_dir) if backup_dir else vault_path.parent / "backups"

    try:
        dest = backup_vault(vault_path, bdir)
        click.echo(f"Backup created: {dest}")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_backup.command(name="restore")
@click.argument("backup_file")
@click.option("--profile", default=None, help="Profile name.")
@click.confirmation_option(prompt="This will overwrite the current vault. Continue?")
def backup_restore(backup_file, profile):
    """Restore vault from a backup file."""
    profile_name = get_profile_name(override=profile)
    vault_path = vault_path_for_profile(profile_name)

    try:
        restore_vault(Path(backup_file), vault_path)
        click.echo("Vault restored successfully.")
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_backup.command(name="list")
@click.option("--profile", default=None, help="Profile name.")
@click.option("--backup-dir", default=None, help="Directory containing backups.")
def backup_list(profile, backup_dir):
    """List available backups."""
    profile_name = get_profile_name(override=profile)
    vault_path = vault_path_for_profile(profile_name)
    bdir = Path(backup_dir) if backup_dir else vault_path.parent / "backups"

    backups = list_backups(bdir)
    if not backups:
        click.echo("No backups found.")
        return
    for b in backups:
        click.echo(str(b))


@cmd_backup.command(name="delete")
@click.argument("backup_file")
def backup_delete(backup_file):
    """Delete a specific backup file."""
    try:
        delete_backup(Path(backup_file))
        click.echo(f"Deleted: {backup_file}")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
