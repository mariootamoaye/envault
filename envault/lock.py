"""Vault locking: prevent concurrent writes by placing a lock file."""

from __future__ import annotations

import os
import time
from pathlib import Path

DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_POLL = 0.1   # seconds


def _lock_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".lock")


def acquire(vault_path: Path, timeout: float = DEFAULT_TIMEOUT, poll: float = DEFAULT_POLL) -> Path:
    """Acquire a lock for *vault_path*.

    Writes a lock file containing the current PID.  Raises ``TimeoutError``
    if the lock cannot be obtained within *timeout* seconds.
    """
    lock = _lock_path(vault_path)
    deadline = time.monotonic() + timeout

    while True:
        try:
            # Exclusive creation — atomic on POSIX
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as fh:
                fh.write(str(os.getpid()))
            return lock
        except FileExistsError:
            if time.monotonic() >= deadline:
                owner = _read_owner(lock)
                raise TimeoutError(
                    f"Vault is locked by PID {owner}. "
                    "Another envault process may be running."
                )
            time.sleep(poll)


def release(lock_path: Path) -> None:
    """Release a previously acquired lock."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def is_locked(vault_path: Path) -> bool:
    """Return True if a lock file exists for *vault_path*."""
    return _lock_path(vault_path).exists()


def _read_owner(lock_path: Path) -> str:
    try:
        return lock_path.read_text().strip()
    except OSError:
        return "unknown"


class VaultLock:
    """Context manager that acquires / releases a vault lock."""

    def __init__(self, vault_path: Path, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._vault_path = vault_path
        self._timeout = timeout
        self._lock_path: Path | None = None

    def __enter__(self) -> "VaultLock":
        self._lock_path = acquire(self._vault_path, timeout=self._timeout)
        return self

    def __exit__(self, *_: object) -> None:
        if self._lock_path is not None:
            release(self._lock_path)
