# Key History

envault records a change log for every key mutation, letting you audit or roll back values over time.

## How It Works

Each vault file (`<profile>.vault.json`) has a sibling history file (`<profile>.vault.history.json`). Every `set` or `unset` operation appends a JSON entry with:

| Field | Description |
|-------|-------------|
| `ts` | ISO-8601 UTC timestamp |
| `key` | Variable name |
| `action` | `set` or `unset` |
| `old` | Previous value (or `null`) |
| `new` | New value (or `null`) |

## API

```python
from envault.history import record_change, read_history, key_history, clear_history
from pathlib import Path

vault = Path(".envault/default.vault.json")

# Record a change
record_change(vault, "API_KEY", "set", old_value=None, new_value="abc123")

# Read all history
entries = read_history(vault)

# Filter by key
for entry in key_history(vault, "API_KEY"):
    print(entry["ts"], entry["action"], entry["new"])

# Clear history
clear_history(vault)
```

## Notes

- History files are **not encrypted**; they store plaintext values. Keep them out of version control.
- Add `*.history.json` to your `.gitignore`.
- Use `clear_history()` to wipe the log when rotating secrets.
