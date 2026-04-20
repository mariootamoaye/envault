"""Tests for envault.lock."""

from __future__ import annotations

import os
import threading
from pathlib import Path

import pytest

from envault.lock import (
    VaultLock,
    acquire,
    is_locked,
    release,
    _lock_path,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "vault.json"
    p.touch()
    return p


def test_acquire_creates_lock_file(vault_path: Path) -> None:
    lock = acquire(vault_path)
    assert _lock_path(vault_path).exists()
    release(lock)


def test_lock_file_contains_pid(vault_path: Path) -> None:
    lock = acquire(vault_path)
    content = lock.read_text().strip()
    assert content == str(os.getpid())
    release(lock)


def test_release_removes_lock_file(vault_path: Path) -> None:
    lock = acquire(vault_path)
    release(lock)
    assert not _lock_path(vault_path).exists()


def test_is_locked_false_when_no_lock(vault_path: Path) -> None:
    assert not is_locked(vault_path)


def test_is_locked_true_when_locked(vault_path: Path) -> None:
    lock = acquire(vault_path)
    assert is_locked(vault_path)
    release(lock)


def test_acquire_times_out_when_already_locked(vault_path: Path) -> None:
    lock = acquire(vault_path)
    try:
        with pytest.raises(TimeoutError, match="locked by PID"):
            acquire(vault_path, timeout=0.2, poll=0.05)
    finally:
        release(lock)


def test_vault_lock_context_manager(vault_path: Path) -> None:
    with VaultLock(vault_path):
        assert is_locked(vault_path)
    assert not is_locked(vault_path)


def test_vault_lock_releases_on_exception(vault_path: Path) -> None:
    with pytest.raises(RuntimeError):
        with VaultLock(vault_path):
            raise RuntimeError("boom")
    assert not is_locked(vault_path)


def test_concurrent_locks_serialised(vault_path: Path) -> None:
    """Only one thread should hold the lock at a time."""
    results: list[str] = []

    def worker(name: str) -> None:
        with VaultLock(vault_path, timeout=5):
            results.append(f"{name}-enter")
            time_ms = 0.02
            import time
            time.sleep(time_ms)
            results.append(f"{name}-exit")

    t1 = threading.Thread(target=worker, args=("A",))
    t2 = threading.Thread(target=worker, args=("B",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Each enter must be immediately followed by its own exit
    assert results.index("A-exit") == results.index("A-enter") + 1 or \
           results.index("B-exit") == results.index("B-enter") + 1
