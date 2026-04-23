"""Notification hooks for envault events (set, unset, rotate, import)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

_SUPPORTED_EVENTS = {"set", "unset", "rotate", "import", "expire"}


def _notify_path(vault_path: Path) -> Path:
    return vault_path.parent / "notify.json"


def load_notify(vault_path: Path) -> dict[str, list[str]]:
    """Return mapping of event -> list of command templates."""
    p = _notify_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_notify(vault_path: Path, config: dict[str, list[str]]) -> None:
    """Persist notification config to disk."""
    _notify_path(vault_path).write_text(json.dumps(config, indent=2))


def add_notify(vault_path: Path, event: str, command: str) -> None:
    """Register *command* to run when *event* fires."""
    if event not in _SUPPORTED_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Supported: {sorted(_SUPPORTED_EVENTS)}")
    config = load_notify(vault_path)
    config.setdefault(event, [])
    if command not in config[event]:
        config[event].append(command)
    save_notify(vault_path, config)


def remove_notify(vault_path: Path, event: str, command: str) -> bool:
    """Remove *command* from *event*. Returns True if it was present."""
    config = load_notify(vault_path)
    cmds = config.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    config[event] = cmds
    save_notify(vault_path, config)
    return True


def fire(vault_path: Path, event: str, context: dict[str, Any] | None = None) -> list[int]:
    """Run all commands registered for *event*.

    *context* values are injected as environment variables prefixed with
    ``ENVAULT_``.  Returns list of return codes.
    """
    config = load_notify(vault_path)
    commands = config.get(event, [])
    env = os.environ.copy()
    env["ENVAULT_EVENT"] = event
    for k, v in (context or {}).items():
        env[f"ENVAULT_{k.upper()}"] = str(v)
    results: list[int] = []
    for cmd in commands:
        rc = subprocess.call(cmd, shell=True, env=env)
        results.append(rc)
    return results
