# Compression

`envault` provides lightweight gzip-based compression helpers for vault data payloads. These utilities are used internally when exporting or sharing large vaults, but can also be used directly.

## Module: `envault.compress`

### `compress_dict(data: dict) -> str`

Serializes the given dictionary to compact JSON, compresses it with gzip (level 9), and returns a **base64-encoded string** suitable for embedding in text-based formats (e.g., bundle files).

```python
from envault.compress import compress_dict

blob = compress_dict({"API_KEY": "secret", "DB_HOST": "localhost"})
print(blob)  # base64 string
```

### `decompress_dict(blob: str) -> dict`

Reverses `compress_dict`. Decodes the base64 string, decompresses the gzip payload, and parses the JSON.

Raises `ValueError` if the input is not valid base64, not valid gzip, or not valid JSON.

```python
from envault.compress import decompress_dict

data = decompress_dict(blob)
print(data["API_KEY"])  # "secret"
```

### `compression_ratio(data: dict) -> float`

Returns the ratio of compressed size to original JSON size. A value less than `1.0` means the compressed form is smaller.

```python
from envault.compress import compression_ratio

ratio = compression_ratio(my_vault_data)
print(f"Compression ratio: {ratio:.2%}")
```

## Error Handling

| Situation | Exception |
|---|---|
| Invalid base64 input | `ValueError: Invalid base64 data: ...` |
| Corrupt gzip payload | `ValueError: Decompression failed: ...` |
| Non-JSON decompressed bytes | `ValueError: JSON parse error after decompression: ...` |

## Notes

- Compression is most effective for large vaults with many repeated key prefixes or long values.
- The output is always a plain ASCII string, safe to store in JSON bundle files.
