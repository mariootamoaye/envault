# Transform

The `transform` module lets you attach value-transformation pipelines to specific vault keys. When you export or apply vault values, each key's transforms are applied in order before the value is used.

## Supported Operations

| Operation | Description | Argument |
|-----------|-------------|----------|
| `upper`   | Convert value to uppercase | — |
| `lower`   | Convert value to lowercase | — |
| `strip`   | Strip leading/trailing whitespace | — |
| `prefix`  | Prepend a string | The prefix string |
| `suffix`  | Append a string | The suffix string |
| `replace` | Replace a substring | `old:new` |

## API

### `add_transform(vault_path, key, op, arg=None)`

Append a transform step to the pipeline for `key`.

```python
from envault.transform import add_transform
add_transform(vault_path, "BASE_URL", "suffix", "/api/v2")
```

Raises `TransformError` if the key is empty or the operation is unknown.

### `remove_transforms(vault_path, key)`

Remove **all** transform steps for `key`. Returns `True` if the key existed, `False` otherwise.

### `apply_transforms(vault_path, key, value)`

Apply the registered pipeline for `key` to `value` and return the result.

```python
from envault.transform import apply_transforms
result = apply_transforms(vault_path, "BASE_URL", "https://example.com")
# → "https://example.com/api/v2"
```

### `apply_all(vault_path, pairs)`

Apply transforms to every key in the `pairs` dict, returning a new dict.

```python
from envault.transform import apply_all
rendered = apply_all(vault_path, store.all())
```

## Storage

Transform rules are stored alongside the vault file as `<vault-stem>.transforms.json`. The file is a JSON object mapping key names to ordered lists of `{op, arg}` steps.

## Example

```bash
# Strip whitespace then uppercase the DB_NAME value on export
envault transform add DB_NAME strip
envault transform add DB_NAME upper
envault export --dotenv
```
