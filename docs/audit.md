# Audit Log

envault records every mutating operation to a local audit log so you can review what changed and when.

## Location

By default the log is stored at:

```
~/.envault/audit.log
```

Each line is a JSON object with the following fields:

| Field     | Description                          |
|-----------|--------------------------------------|
| `ts`      | ISO-8601 timestamp (UTC)             |
| `action`  | Operation performed (`set`, `unset`, `import`, etc.) |
| `profile` | Vault profile name                   |
| `key`     | Variable name (omitted for bulk ops) |

## Example entries

```json
{"ts": "2024-05-01T12:00:00+00:00", "action": "set", "profile": "default", "key": "DATABASE_URL"}
{"ts": "2024-05-01T12:01:00+00:00", "action": "unset", "profile": "default", "key": "OLD_SECRET"}
{"ts": "2024-05-01T12:02:00+00:00", "action": "import", "profile": "staging"}
```

## Programmatic access

```python
from envault.audit import read, clear

entries = read()
for e in entries:
    print(e["ts"], e["action"], e.get("key", "-"))

# Remove the log
clear()
```

## Notes

- The audit log is **local only** and never synced or encrypted.
- It is append-only; entries are never modified after being written.
- Use `clear()` to rotate or remove the log manually.
