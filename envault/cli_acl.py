"""CLI commands for managing access control lists."""

from __future__ import annotations

from pathlib import Path

import click

from envault.acl import (
    can_access,
    list_roles,
    load_acl,
    remove_role,
    set_permission,
)
from envault.profile import vault_path_for_profile


@click.group("acl")
def cmd_acl() -> None:
    """Manage per-role access control lists."""


@cmd_acl.command("grant")
@click.argument("role")
@click.argument("action", type=click.Choice(["read", "write"]))
@click.argument("keys", nargs=-1, required=True)
@click.option("--profile", default=None, help="Vault profile to target.")
def acl_grant(role: str, action: str, keys: tuple, profile: str | None) -> None:
    """Grant ROLE permission to perform ACTION on the listed KEYS."""
    vault_dir = vault_path_for_profile(profile).parent
    set_permission(vault_dir, role, action, list(keys))
    click.echo(f"Granted {action} on {list(keys)} to role '{role}'.")


@cmd_acl.command("revoke")
@click.argument("role")
@click.option("--profile", default=None)
def acl_revoke(role: str, profile: str | None) -> None:
    """Remove ROLE from the ACL entirely."""
    vault_dir = vault_path_for_profile(profile).parent
    remove_role(vault_dir, role)
    click.echo(f"Role '{role}' removed from ACL.")


@cmd_acl.command("list")
@click.option("--profile", default=None)
def acl_list(profile: str | None) -> None:
    """List all roles and their permissions."""
    vault_dir = vault_path_for_profile(profile).parent
    acl = load_acl(vault_dir)
    if not acl:
        click.echo("No ACL entries defined.")
        return
    for role, perms in acl.items():
        for action, keys in perms.items():
            keys_str = ", ".join(keys) if keys else "(none)"
            click.echo(f"{role}  {action:5s}  {keys_str}")


@cmd_acl.command("check")
@click.argument("role")
@click.argument("action", type=click.Choice(["read", "write"]))
@click.argument("key")
@click.option("--profile", default=None)
def acl_check(role: str, action: str, key: str, profile: str | None) -> None:
    """Check whether ROLE can perform ACTION on KEY."""
    vault_dir = vault_path_for_profile(profile).parent
    allowed = can_access(vault_dir, role, action, key)
    if allowed:
        click.echo(f"ALLOW: '{role}' may {action} '{key}'.")
    else:
        click.echo(f"DENY: '{role}' may not {action} '{key}'.")
        raise SystemExit(1)
