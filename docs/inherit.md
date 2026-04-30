# Vault Inheritance

envault supports **profile inheritance**: you can define a chain of profiles
and resolve a key by walking from the most-specific to the least-specific
profile until a value is found.

This is useful for layered configurations such as:

```
prod  →  staging  →  base
```

## API

### `resolve(key, chain, password, base_dir=None) -> InheritResult`

Walk `chain` (ordered most-specific first) and return the first profile
that contains `key`.

```python
from envault.inherit import resolve

result = resolve(
    key="DB_URL",
    chain=["prod", "staging", "base"],
    password="s3cr3t",
)

if result.found:
    print(f"{result.key} = {result.value}  (from '{result.resolved_from}')")
else:
    print(f"{result.key} not found in any profile")
```

#### `InheritResult` fields

| Field            | Type            | Description                              |
|------------------|-----------------|------------------------------------------|
| `key`            | `str`           | The key that was looked up               |
| `value`          | `str \| None`   | Resolved value, or `None` if not found   |
| `resolved_from`  | `str \| None`   | Profile name where the value was found   |
| `chain`          | `list[str]`     | The full chain that was walked           |
| `found`          | `bool`          | Convenience property (`value is not None`) |

### `resolve_all(chain, password, base_dir=None) -> dict[str, InheritResult]`

Return a merged view of **all** keys across the chain.  Each key is
attributed to the most-specific profile that defines it.

```python
from envault.inherit import resolve_all

merged = resolve_all(
    chain=["prod", "base"],
    password="s3cr3t",
)

for key, result in merged.items():
    print(f"{key} = {result.value}  [{result.resolved_from}]")
```

## Behaviour

- Profiles that have no vault file on disk are **silently skipped**.
- The chain is ordered **most-specific first**; the first profile that
  contains a key wins.
- All profiles in a chain must share the **same password**.
