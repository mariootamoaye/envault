"""CLI commands for vault snapshots."""
import click
from envault.cli import _get_store, _prompt_password
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot


@click.group("snapshot")
def cmd_snapshot():
    """Manage vault snapshots."""


@cmd_snapshot.command("create")
@click.option("--profile", default=None)
@click.option("--label", default="", help="Optional label for this snapshot.")
def snap_create(profile, label):
    """Create a snapshot of the current vault state."""
    store = _get_store(profile)
    password = _prompt_password(confirm=False)
    name = create_snapshot(store, password, label=label)
    click.echo(f"Snapshot created: {name}")


@cmd_snapshot.command("list")
@click.option("--profile", default=None)
def snap_list(profile):
    """List available snapshots."""
    store = _get_store(profile)
    snaps = list_snapshots(store)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" ({s['label']})" if s["label"] else ""
        click.echo(f"{s['file']}{label}  [{s['keys']} keys]")


@cmd_snapshot.command("restore")
@click.argument("filename")
@click.option("--profile", default=None)
def snap_restore(filename, profile):
    """Restore vault from a snapshot."""
    store = _get_store(profile)
    password = _prompt_password(confirm=False)
    count = restore_snapshot(store, password, filename)
    click.echo(f"Restored {count} keys from {filename}.")


@cmd_snapshot.command("delete")
@click.argument("filename")
@click.option("--profile", default=None)
def snap_delete(filename, profile):
    """Delete a snapshot."""
    store = _get_store(profile)
    removed = delete_snapshot(store, filename)
    if removed:
        click.echo(f"Deleted snapshot {filename}.")
    else:
        click.echo(f"Snapshot {filename} not found.", err=True)
