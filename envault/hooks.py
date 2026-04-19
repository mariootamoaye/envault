"""Pre/post hooks for vault operations."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

HOOK_FILE = ".envault-hooks.json"

_VALID_EVENTS = {"pre-set", "post-set", "pre-unset", "post-unset", "post-import"}


def _hooks_path(vault_dir: Path) -> Path:
    return vault_dir / HOOK_FILE


def load_hooks(vault_dir: Path) -> Dict[str, List[str]]:
    """Load hooks config from vault directory."""
    path = _hooks_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if k in _VALID_EVENTS}


def save_hooks(vault_dir: Path, hooks: Dict[str, List[str]]) -> None:
    """Persist hooks config to vault directory."""
    invalid = set(hooks) - _VALID_EVENTS
    if invalid:
        raise ValueError(f"Unknown hook events: {invalid}")
    path = _hooks_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(hooks, f, indent=2)


def add_hook(vault_dir: Path, event: str, command: str) -> None:
    """Register a shell command for a hook event."""
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {sorted(_VALID_EVENTS)}")
    hooks = load_hooks(vault_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    save_hooks(vault_dir, hooks)


def remove_hook(vault_dir: Path, event: str, command: str) -> bool:
    """Remove a hook command. Returns True if it existed."""
    hooks = load_hooks(vault_dir)
    cmds = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    if not cmds:
        del hooks[event]
    save_hooks(vault_dir, hooks)
    return True


def fire(vault_dir: Path, event: str, env: Optional[Dict[str, str]] = None) -> List[int]:
    """Run all commands registered for an event. Returns list of exit codes."""
    hooks = load_hooks(vault_dir)
    commands = hooks.get(event, [])
    results: List[int] = []
    merged_env = {**os.environ, **(env or {})}
    for cmd in commands:
        code = os.system(cmd) if not env else _run_with_env(cmd, merged_env)
        results.append(code)
    return results


def _run_with_env(cmd: str, env: Dict[str, str]) -> int:
    import subprocess
    result = subprocess.run(cmd, shell=True, env=env)
    return result.returncode
