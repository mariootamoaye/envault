"""CLI commands for template rendering."""
import click
from envault.cli import _get_store, _prompt_password
from envault.template import render_file, check_template, RenderError


@click.group(name="template")
def cmd_template():
    """Render templates using vault variables."""


@cmd_template.command(name="render")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--output", "-o", default="-", help="Output file (default: stdout)")
@click.option("--profile", default=None, help="Vault profile to use")
@click.option("--non-strict", is_flag=True, default=False, help="Leave missing vars as-is")
def template_render(template_file, output, profile, non_strict):
    """Render TEMPLATE_FILE substituting vault variables."""
    password = _prompt_password()
    store = _get_store(password, profile)
    variables = {k: store.get(k) for k in store.keys()}
    strict = not non_strict
    try:
        result = render_file(template_file, variables, strict=strict)
    except RenderError as exc:
        raise click.ClickException(str(exc))
    if output == "-":
        click.echo(result, nl=False)
    else:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Written to {output}")


@cmd_template.command(name="check")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--profile", default=None, help="Vault profile to use")
def template_check(template_file, profile):
    """Check which variables in TEMPLATE_FILE are present in the vault."""
    password = _prompt_password()
    store = _get_store(password, profile)
    variables = {k: store.get(k) for k in store.keys()}
    with open(template_file) as fh:
        template = fh.read()
    results = check_template(template, variables)
    if not results:
        click.echo("No variables referenced in template.")
        return
    for name, status in results:
        icon = "✓" if status == "ok" else "✗"
        click.echo(f"  {icon} {name} ({status})")
    missing = [n for n, s in results if s == "missing"]
    if missing:
        raise click.ClickException(f"{len(missing)} variable(s) missing from vault.")
