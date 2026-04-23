# Redaction

envault can automatically hide sensitive values in any output — logs, diffs,
exports — based on configurable rules.

## How it works

A key is considered **redacted** if:

1. Its name matches one of the configured **regex patterns**, OR
2. It has been **explicitly pinned** as sensitive.

By default envault ships with a built-in pattern that matches common
sensitive names such as `PASSWORD`, `SECRET`, `TOKEN`, `API_KEY`, `AUTH`,
`CREDENTIAL`, and `PRIVATE`.

Redact configuration is stored per-vault in `redact.json` alongside the
encrypted vault file.

## API

```python
from envault.redact import (
    is_redacted,
    pin_key,
    unpin_key,
    add_pattern,
    redact_dict,
    load_redact,
)
```

### `is_redacted(vault_path, key) -> bool`

Returns `True` if `key` is considered sensitive under the current rules.

### `pin_key(vault_path, key)`

Explicitly mark `key` as redacted regardless of pattern matching.

### `unpin_key(vault_path, key)`

Remove an explicit redaction mark.  Pattern-based matching still applies.

### `add_pattern(vault_path, pattern)`

Add a regex pattern.  Any key whose name matches the pattern will be
treated as redacted.  Raises `re.error` for invalid patterns.

### `redact_dict(vault_path, data, placeholder="**REDACTED**") -> dict`

Return a copy of `data` with sensitive values replaced by `placeholder`.
The original mapping is never mutated.

## Example

```python
from pathlib import Path
from envault.redact import redact_dict, pin_key

vault = Path(".envault/default.enc")
pin_key(vault, "STRIPE_WEBHOOK_SECRET")

env = {
    "DATABASE_URL": "postgres://...",
    "STRIPE_WEBHOOK_SECRET": "whsec_...",
    "API_KEY": "sk-...",
}

safe = redact_dict(vault, env)
# safe == {
#   "DATABASE_URL": "postgres://...",
#   "STRIPE_WEBHOOK_SECRET": "**REDACTED**",
#   "API_KEY": "**REDACTED**",
# }
```
