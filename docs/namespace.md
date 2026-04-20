# Namespace Support

envault supports grouping related keys under a **namespace** prefix, making it
easy to manage sets of variables for different services or components.

## Key format

Namespaced keys follow the pattern:

```
<NAMESPACE>__<KEY>
```

Both the namespace and key are stored in upper-case. The double-underscore
(`__`) separator was chosen to avoid conflicts with single-underscore
conventions common in environment variable names.

**Example:**

```
APP__DATABASE_URL
APP__SECRET_KEY
DB__HOST
DB__PORT
```

## Python API

```python
from envault.namespace import (
    make_key, split_key, list_namespaces,
    keys_in_namespace, get_namespace, delete_namespace,
)

# Build a namespaced key
full_key = make_key("app", "secret_key")   # -> "APP__SECRET_KEY"

# Decompose a namespaced key
ns, key = split_key("APP__SECRET_KEY")     # -> ("APP", "SECRET_KEY")

# Discover all namespaces in a store
namespaces = list_namespaces(store)        # -> ["APP", "DB", ...]

# List all full keys in a namespace
keys = keys_in_namespace(store, "APP")     # -> ["APP__SECRET_KEY", ...]

# Retrieve all values in a namespace as {short_key: value}
data = get_namespace(store, "APP")         # -> {"SECRET_KEY": "...", ...}

# Remove all keys in a namespace; returns count removed
count = delete_namespace(store, "APP")
```

## Notes

- Namespace and key names are **normalised to upper-case** automatically.
- Keys without the `__` separator are treated as non-namespaced and are
  ignored by namespace-aware functions.
- Namespaces are purely a naming convention enforced by the helper module;
  the underlying vault store is unaware of them.
