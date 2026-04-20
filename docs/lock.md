# Vault Locking

envault uses a **file-based lock** to prevent two processes from writing to the
same vault simultaneously, which could corrupt the encrypted store.

## How it works

Whenever envault needs to modify a vault it places a `.lock` file next to the
vault file (e.g. `~/.envault/default.lock`).  The lock file contains the PID of
the owning process.  Once the operation is complete the lock file is removed.

## Automatic locking

All write commands (`set`, `unset`, `import`, `rotate`, …) acquire the lock
automatically.  You do not need to manage locks manually.

## Timeout

If the lock cannot be acquired within **10 seconds** (default) envault exits
with an error message that includes the PID of the process currently holding
the lock:

```
Error: Vault is locked by PID 12345. Another envault process may be running.
```

If the owning process has crashed and left a stale lock you can remove it
manually:

```bash
rm ~/.envault/default.lock
```

## Python API

```python
from pathlib import Path
from envault.lock import VaultLock

vault = Path("/path/to/vault.json")

with VaultLock(vault, timeout=5):
    # safe to read and write
    ...
```

### Low-level helpers

| Function | Description |
|---|---|
| `acquire(vault_path, timeout, poll)` | Acquire lock; returns lock `Path` |
| `release(lock_path)` | Release a lock |
| `is_locked(vault_path)` | Check whether a lock exists |
