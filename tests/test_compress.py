"""Tests for envault.compress."""

from __future__ import annotations

import pytest

from envault.compress import compress_dict, decompress_dict, compression_ratio


SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "supersecretvalue",
    "API_KEY": "abc123xyz",
}


def test_compress_returns_string():
    result = compress_dict(SAMPLE)
    assert isinstance(result, str)
    assert len(result) > 0


def test_compress_is_base64():
    import base64
    result = compress_dict(SAMPLE)
    # Should not raise
    decoded = base64.b64decode(result)
    assert isinstance(decoded, bytes)


def test_roundtrip_simple():
    result = compress_dict(SAMPLE)
    restored = decompress_dict(result)
    assert restored == SAMPLE


def test_roundtrip_empty_dict():
    result = compress_dict({})
    assert decompress_dict(result) == {}


def test_roundtrip_nested_values():
    data = {"KEY": "value with spaces and \nnewlines", "NUM": "42"}
    assert decompress_dict(compress_dict(data)) == data


def test_decompress_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid base64"):
        decompress_dict("!!!not-base64!!!")


def test_decompress_invalid_gzip_raises():
    import base64
    # Valid base64 but not gzip data
    bad = base64.b64encode(b"this is not gzip").decode()
    with pytest.raises(ValueError, match="Decompression failed"):
        decompress_dict(bad)


def test_decompress_invalid_json_raises():
    import base64
    import gzip
    # Valid gzip but not JSON
    bad = base64.b64encode(gzip.compress(b"not json")).decode()
    with pytest.raises(ValueError, match="JSON parse error"):
        decompress_dict(bad)


def test_compression_ratio_is_float():
    ratio = compression_ratio(SAMPLE)
    assert isinstance(ratio, float)


def test_compression_ratio_large_repetitive_data():
    # Highly repetitive data should compress well (ratio < 1)
    data = {f"KEY_{i}": "AAAAAAAAAAAAAAAAAAAAAAAAAAAA" for i in range(50)}
    ratio = compression_ratio(data)
    assert ratio < 1.0


def test_compression_ratio_empty_dict():
    # Edge case: empty dict; should return 1.0 (no original bytes)
    ratio = compression_ratio({})
    assert ratio == 1.0
