"""Compression utilities for vault data — gzip-based compress/decompress helpers."""

from __future__ import annotations

import gzip
import json
import base64
from typing import Any


def compress_dict(data: dict[str, Any]) -> str:
    """Serialize *data* to JSON, gzip-compress it, and return a base64 string."""
    raw = json.dumps(data, separators=(",", ":")).encode()
    compressed = gzip.compress(raw, compresslevel=9)
    return base64.b64encode(compressed).decode()


def decompress_dict(blob: str) -> dict[str, Any]:
    """Reverse of :func:`compress_dict` — decode base64, decompress, parse JSON.

    Raises
    ------
    ValueError
        If *blob* is not valid base64 or the decompressed bytes are not valid JSON.
    """
    try:
        compressed = base64.b64decode(blob)
    except Exception as exc:
        raise ValueError(f"Invalid base64 data: {exc}") from exc

    try:
        raw = gzip.decompress(compressed)
    except Exception as exc:
        raise ValueError(f"Decompression failed: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON parse error after decompression: {exc}") from exc


def compression_ratio(data: dict[str, Any]) -> float:
    """Return the compression ratio (compressed / original) for *data*.

    A value < 1.0 means the compressed form is smaller.
    """
    original = json.dumps(data, separators=(",", ":")).encode()
    compressed = gzip.compress(original, compresslevel=9)
    if not original:
        return 1.0
    return len(compressed) / len(original)
