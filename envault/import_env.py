"""Import environment variables from .env files or current environment into the vault."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Optional


_DOTENV_LINE = re.compile(
    r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$"
)


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (
            value[0] == "'" and value[-1] == "'"
        ):
            return value[1:-1]
    return value


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse dotenv-formatted text and return a dict of key/value pairs."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _DOTENV_LINE.match(line)
        if match:
            key, value = match.group(1), match.group(2).strip()
            result[key] = _strip_quotes(value)
    return result


def import_from_file(path: Path) -> Dict[str, str]:
    """Read a .env file and return parsed key/value pairs."""
    text = path.read_text(encoding="utf-8")
    return parse_dotenv(text)


def import_from_env(keys: Optional[list[str]] = None) -> Dict[str, str]:
    """Return variables from the current process environment.

    If *keys* is given, only those keys are returned.
    """
    env = dict(os.environ)
    if keys is not None:
        env = {k: v for k, v in env.items() if k in keys}
    return env
