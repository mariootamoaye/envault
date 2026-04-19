"""Export vault secrets to various shell formats."""
from __future__ import annotations

from typing import Dict


SUPPORTED_FORMATS = ("dotenv", "bash", "fish")


def _quote(value: str) -> str:
    """Wrap value in single quotes, escaping any single quotes within."""
    return "'" + value.replace("'", "'\\''" ) + "'"


def export_dotenv(secrets: Dict[str, str]) -> str:
    """Render secrets as a .env file."""
    lines = []
    for key, value in sorted(secrets.items()):
        lines.append(f"{key}={_quote(value)}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_bash(secrets: Dict[str, str]) -> str:
    """Render secrets as bash export statements."""
    lines = []
    for key, value in sorted(secrets.items()):
        lines.append(f"export {key}={_quote(value)}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_fish(secrets: Dict[str, str]) -> str:
    """Render secrets as fish shell set statements."""
    lines = []
    for key, value in sorted(secrets.items()):
        lines.append(f"set -x {key} {_quote(value)}")
    return "\n".join(lines) + ("\n" if lines else "")


def render(secrets: Dict[str, str], fmt: str) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "dotenv":
        return export_dotenv(secrets)
    if fmt == "bash":
        return export_bash(secrets)
    if fmt == "fish":
        return export_fish(secrets)
    raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
