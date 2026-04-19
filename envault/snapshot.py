"""Snapshot: capture and restore vault state at a point in time."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

from envault.store import VaultStore


def _snapshots_dir(vault_path: Path) -> Path:
    d = vault_path.parent / ".snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_snapshot(store: VaultStore, password: str, label: str = "") -> str:
    """Dump all decrypted keys into a timestamped snapshot file.
    Returns the snapshot filename."""
    data = {k: store.get(k, password) for k in store.keys()}
    ts = int(time.time())
    entry = {"ts": ts, "label": label, "data": data}
    snapshots_dir = _snapshots_dir(Path(store.path))
    name = f"{ts}.json"
    (snapshots_dir / name).write_text(json.dumps(entry))
    return name


def list_snapshots(store: VaultStore) -> List[Dict]:
    """Return snapshot metadata sorted newest-first."""
    snapshots_dir = _snapshots_dir(Path(store.path))
    results = []
    for f in sorted(snapshots_dir.glob("*.json"), reverse=True):
        raw = json.loads(f.read_text())
        results.append({"file": f.name, "ts": raw["ts"], "label": raw.get("label", ""), "keys": len(raw["data"])})
    return results


def restore_snapshot(store: VaultStore, password: str, filename: str) -> int:
    """Restore all keys from a snapshot. Returns number of keys restored."""
    snapshots_dir = _snapshots_dir(Path(store.path))
    raw = json.loads((snapshots_dir / filename).read_text())
    data: Dict[str, str] = raw["data"]
    for k, v in data.items():
        store.set(k, v, password)
    store.save()
    return len(data)


def delete_snapshot(store: VaultStore, filename: str) -> bool:
    snapshots_dir = _snapshots_dir(Path(store.path))
    target = snapshots_dir / filename
    if target.exists():
        target.unlink()
        return True
    return False
