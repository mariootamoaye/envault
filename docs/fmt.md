# Value Formatting (`envault.fmt`)

The `envault.fmt` module provides helpers for rendering vault key/value data
in human-readable formats — useful for CLI output, debugging, and reports.

---

## Functions

### `infer_type(value: str) -> str`

Inspects a string value and returns a label describing its apparent type:

| Label    | Condition                                      |
|----------|------------------------------------------------|
| `bool`   | `true`, `false`, `yes`, `no`, `1`, `0`, `on`, `off` |
| `int`    | Parseable as an integer                        |
| `float`  | Parseable as a floating-point number           |
| `url`    | Starts with `http://` or `https://`            |
| `secret` | Long base64-like string (≥ 20 chars)           |
| `str`    | Anything else                                  |

```python
from envault.fmt import infer_type

infer_type("true")              # "bool"
infer_type("3.14")              # "float"
infer_type("https://api.io")    # "url"
```

---

### `truncate(value, max_len=40, placeholder="...") -> str`

Shortens a string to at most `max_len` characters. If truncated, the string
ends with `placeholder`.

```python
from envault.fmt import truncate

truncate("a very long value that exceeds the limit", max_len=20)
# "a very long value..."
```

---

### `format_row(key, value, show_type=False, max_val=40) -> str`

Formats a single key/value entry as a padded display string. Pass
`show_type=True` to append the inferred type label.

---

### `format_table(data, show_type=False, max_val=40) -> str`

Renders an entire `dict[str, str]` as an aligned, sorted table.
Returns `"(empty)"` for an empty dict.

```python
from envault.fmt import format_table

print(format_table({"DB_HOST": "localhost", "PORT": "5432"}, show_type=True))
```

Example output:

```
KEY                             VALUE                                       TYPE
--------------------------------------------------------------------------------
DB_HOST                         localhost                                   str
PORT                            5432                                        int
```

---

### `format_pairs(data) -> list[tuple[str, str, str]]`

Returns a sorted list of `(key, truncated_value, type)` tuples — useful when
you need structured data rather than a pre-rendered string.

```python
from envault.fmt import format_pairs

for key, val, typ in format_pairs(vault_data):
    print(f"{key} ({typ}): {val}")
```
