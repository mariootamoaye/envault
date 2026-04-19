"""Watch a vault for changes and run a command when variables change."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Callable, Optional

from envault.store import VaultStore


def _vault_hash(store: VaultStore) -> str:
    """Return a hash representing the current state of the vault."""
    raw = json.dumps(store.all(), sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def watch(
    store: VaultStore,
    password: str,
    command: list[str],
    interval: float = 2.0,
    on_change: Optional[Callable[[dict], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll the vault and re-run *command* whenever its contents change.

    Parameters
    ----------
    store:          VaultStore to monitor.
    password:       Password used to reload the store on each poll.
    command:        Shell command to execute on change (passed to subprocess).
    interval:       Seconds between polls.
    on_change:      Optional callback receiving the new env dict.
    max_iterations: Stop after this many iterations (useful for tests).
    """
    store.load(password)
    last_hash = _vault_hash(store)
    iterations = 0

    while True:
        time.sleep(interval)
        store.load(password)
        current_hash = _vault_hash(store)

        if current_hash != last_hash:
            last_hash = current_hash
            env_data = store.all()
            if on_change:
                on_change(env_data)
            if command:
                subprocess.run(command, check=False)  # noqa: S603

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
