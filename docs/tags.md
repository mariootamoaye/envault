# Tags

envault supports tagging vault keys so you can group and filter them by category.

## Concepts

Tags are free-form strings associated with a key (e.g. `db`, `prod`, `secret`).
Tag metadata is stored alongside your variables in the vault under a reserved
prefix (`__tags__.<KEY>`) and is encrypted like any other value.

## Python API

```python
from envault.tags import set_tags, get_tags, keys_by_tag, all_tags, remove_tags

# Assign tags
set_tags(store, "DB_URL", ["db", "prod"])

# Read tags for a key
print(get_tags(store, "DB_URL"))  # ['db', 'prod']

# Find all keys with a given tag
print(keys_by_tag(store, "prod"))  # ['DB_URL', ...]

# Overview of all tagged keys
print(all_tags(store))  # {'DB_URL': ['db', 'prod'], ...}

# Remove tags from a key
remove_tags(store, "DB_URL")
```

## Notes

- Tags are stored sorted and deduplicated.
- Removing a key from the vault does **not** automatically remove its tag
  metadata — call `remove_tags()` alongside `store.unset()` to keep things tidy.
- The `__tags__.*` namespace is reserved; avoid using it for regular variables.
