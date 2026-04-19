"""Tests for envault.watch."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.store import VaultStore
from envault.watch import _vault_hash, watch

PASSWORD = "test-password"


@pytest.fixture()
def store(tmp_path: Path) -> VaultStore:
    s = VaultStore(tmp_path / "vault.enc")
    s.load(PASSWORD)  # initialise empty
    return s


def test_vault_hash_stable(store: VaultStore) -> None:
    store.set("KEY", "value", PASSWORD)
    h1 = _vault_hash(store)
    h2 = _vault_hash(store)
    assert h1 == h2


def test_vault_hash_changes_on_update(store: VaultStore) -> None:
    store.set("A", "1", PASSWORD)
    h1 = _vault_hash(store)
    store.set("A", "2", PASSWORD)
    h2 = _vault_hash(store)
    assert h1 != h2


def test_watch_calls_on_change_when_vault_modified(tmp_path: Path) -> None:
    s = VaultStore(tmp_path / "vault.enc")
    s.load(PASSWORD)
    s.set("FOO", "bar", PASSWORD)

    changes: list[dict] = []
    call_count = 0

    def fake_load(pw: str) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Second load simulates an external change
            s.set("FOO", "baz", PASSWORD)

    s.load = fake_load  # type: ignore[method-assign]

    with patch("envault.watch.time.sleep"):
        watch(s, PASSWORD, command=[], on_change=changes.append, max_iterations=1)

    assert len(changes) == 1
    assert changes[0].get("FOO") == "baz"


def test_watch_no_change_does_not_call_callback(store: VaultStore) -> None:
    store.set("X", "1", PASSWORD)
    changes: list[dict] = []

    original_load = store.load

    with patch("envault.watch.time.sleep"):
        watch(store, PASSWORD, command=[], on_change=changes.append, max_iterations=1)

    assert changes == []


def test_watch_runs_command_on_change(tmp_path: Path) -> None:
    s = VaultStore(tmp_path / "vault.enc")
    s.load(PASSWORD)
    s.set("K", "v", PASSWORD)

    call_count = 0

    def fake_load(pw: str) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            s.set("K", "changed", PASSWORD)

    s.load = fake_load  # type: ignore[method-assign]

    with patch("envault.watch.time.sleep"), patch("envault.watch.subprocess.run") as mock_run:
        watch(s, PASSWORD, command=["echo", "hi"], max_iterations=1)

    mock_run.assert_called_once_with(["echo", "hi"], check=False)
