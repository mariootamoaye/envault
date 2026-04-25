# Validation

envault supports per-key validation rules so you can catch bad values before they reach your application.

## Overview

Rules are stored in `.envault_validate.json` alongside the vault file. Each rule specifies a **type**, an optional **regex pattern**, and whether the key is **required**.

## Supported Types

| Type    | Description                                  |
|---------|----------------------------------------------|
| `str`   | Any string (default)                         |
| `int`   | Must be parseable as an integer              |
| `float` | Must be parseable as a floating-point number |
| `bool`  | `true`, `false`, `1`, `0`, `yes`, `no`       |
| `url`   | Must start with `http://` or `https://`      |
| `email` | Basic `user@domain.tld` check                |
| `regex` | Validated only against `pattern` if set      |

## API

### `set_rule(vault_path, key, type_, pattern=None, required=False)`

Create or update a validation rule for `key`.

```python
from envault.validate import set_rule

set_rule(vault_path, "PORT", "int", required=True)
set_rule(vault_path, "COLOR", "str", pattern=r"^#[0-9a-fA-F]{6}$")
```

Raises `ValueError` if the type is unknown or the pattern is an invalid regex.

### `remove_rule(vault_path, key)`

Delete the rule for `key`. Returns `True` if removed, `False` if it did not exist.

### `validate_store(vault_path, data)`

Validate all keys in `data` against stored rules. Returns a list of `ValidationError` objects.

```python
from envault.validate import validate_store

errors = validate_store(vault_path, {"PORT": "abc"})
for e in errors:
    print(e)  # PORT: [type] expected int, got 'abc'
```

### `validate_value(key, value, rule)`

Validate a single `value` against a rule dict. Useful for inline checks.

## Errors

Each `ValidationError` has:

- `key` — the vault key that failed
- `rule` — the rule that triggered (`type`, `pattern`, `required`)
- `message` — human-readable explanation

`str(error)` returns a formatted string suitable for CLI output.
