"""CLI commands for diffing vaults or comparing vault to .env file."""
import click
from envault.cli import _get_store, _prompt_password
from envault.diff import diff_store_dotenv, diff_stores, format_diff
from envault.profile import vault_path_for_profile
from envault.store import VaultStore


@click.group(name="diff")
def cmd_diff():
    """Compare vault contents."""


@cmd_diff.command(name="dotenv")
@click.argument("dotenv_file", type=click.Path(exists=True))
@click.option("--profile", default=None, help="Vault profile to use.")
@click.option("--show-values", is_flag=True, default=False, help="Show values in diff output.")
@click.pass_context
def diff_dotenv(ctx, dotenv_file, profile, show_values):
    """Diff vault against a .env file."""
    store = _get_store(profile)
    password = _prompt_password()
    try:
        entries = diff_store_dotenv(store, password, dotenv_file)
    except Exception as exc:
        raise click.ClickException(str(exc))
    if not entries:
        click.echo("(empty)")
        return
    click.echo(format_diff(entries, show_values=show_values))


@cmd_diff.command(name="profiles")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--show-values", is_flag=True, default=False)
def diff_profiles(profile_a, profile_b, show_values):
    """Diff two vault profiles."""
    store_a = VaultStore(vault_path_for_profile(profile_a))
    store_b = VaultStore(vault_path_for_profile(profile_b))
    password_a = _prompt_password(f"Password for profile '{profile_a}': ")
    password_b = _prompt_password(f"Password for profile '{profile_b}': ")
    try:
        entries = diff_stores(store_a, password_a, store_b, password_b)
    except Exception as exc:
        raise click.ClickException(str(exc))
    if not entries:
        click.echo("(empty)")
        return
    click.echo(format_diff(entries, show_values=show_values))
