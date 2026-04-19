"""CLI command for exporting vault secrets to shell-friendly formats."""
from __future__ import annotations

import sys
import click

from envault.cli import _get_store, _prompt_password
from envault.export import render, SUPPORTED_FORMATS


@click.command("export")
@click.option(
    "--format", "-f",
    "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(list(SUPPORTED_FORMATS)),
    help="Output format.",
)
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
def cmd_export(fmt: str, vault_path: str, output: str | None) -> None:
    """Decrypt and export all secrets in the vault."""
    password = _prompt_password(confirm=False)
    store = _get_store(vault_path, password)

    try:
        secrets = store.all()
    except Exception as exc:  # pragma: no cover
        click.echo(f"Error reading vault: {exc}", err=True)
        sys.exit(1)

    if not secrets:
        click.echo("Vault is empty.", err=True)
        return

    rendered = render(secrets, fmt)

    if output:
        with open(output, "w") as fh:
            fh.write(rendered)
        click.echo(f"Exported {len(secrets)} variable(s) to {output}")
    else:
        click.echo(rendered, nl=False)
