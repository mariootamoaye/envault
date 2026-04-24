# Scope

Scopes let you tag each key with a logical environment label such as `prod`, `ci`, or `local`. You can then filter exports, diffs, or cascades to a specific scope.

## Concepts

- A **scope** is a free-form string label (e.g. `prod`, `staging`, `ci`).
- Each key can belong to **at most one** scope at a time.
- Scope metadata is stored alongside the vault in a `<vault>.scopes.json` sidecar file.

## Python API

```python
from pathlib import Path
from envault.scope import set_scope, remove_scope, keys_in_scope, list_scopes, filter_by_scope

vault = Path("vault.json")

# Assign a scope
set_scope(vault, "API_KEY", "prod")
set_scope(vault, "CI_TOKEN", "ci")

# Query
print(keys_in_scope(vault, "prod"))   # ['API_KEY']
print(list_scopes(vault))             # ['ci', 'prod']

# Filter a dict to only prod keys
data = {"API_KEY": "secret", "CI_TOKEN": "tok", "DEBUG": "1"}
print(filter_by_scope(data, vault, "prod"))  # {'API_KEY': 'secret'}

# Remove
remove_scope(vault, "API_KEY")
```

## CLI

### Assign a key to a scope

```bash
envault scope set API_KEY prod
```

### Remove a scope assignment

```bash
envault scope unset API_KEY
```

### List all keys with their scopes

```bash
envault scope list
```

### List keys in a specific scope

```bash
envault scope list --scope prod
```

### Show all distinct scope names

```bash
envault scope scopes
```

## Notes

- Scope names are case-sensitive (`Prod` ≠ `prod`).
- Deleting a key from the vault does **not** automatically remove its scope entry; call `scope unset` explicitly.
- Scopes are purely metadata — they do not affect encryption or storage of the actual values.
