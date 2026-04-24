# Blame

The **blame** feature records which user and host last modified each key in a vault, along with a UTC timestamp. This is useful for auditing who changed a sensitive variable in a shared team environment.

## Storage

Blame data is stored in a sidecar file next to the vault:

```
vault.json        ← encrypted secrets
vault.blame.json  ← blame metadata (plaintext)
```

Each entry in the blame file looks like:

```json
{
  "MY_API_KEY": {
    "user": "alice",
    "host": "dev-laptop.local",
    "timestamp": "2024-06-01T12:34:56+00:00"
  }
}
```

## API

### `record_blame(vault_path, key, *, user=None, host=None) -> dict`

Record that `key` was last modified right now. If `user` or `host` are omitted, they are inferred from the `USER` / `USERNAME` environment variable and `socket.gethostname()` respectively.

```python
from envault.blame import record_blame

record_blame(Path("~/.envault/default.json"), "DATABASE_URL")
```

### `get_blame(vault_path, key) -> dict | None`

Return the blame entry for `key`, or `None` if no record exists.

### `remove_blame(vault_path, key) -> bool`

Delete the blame record for `key`. Returns `True` if an entry was removed.

### `format_blame(entry) -> str`

Return a human-readable summary such as `alice@dev-laptop.local on 2024-06-01T12:34:56+00:00`.

## Integration

Blame recording is typically called automatically by the CLI `set` and `unset` commands so that every mutation is attributed without extra effort from the user.
