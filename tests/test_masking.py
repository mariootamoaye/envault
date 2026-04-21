"""Tests for envault.masking."""

import pytest
from envault.masking import (
    mask_value,
    mask_dict,
    format_masked_table,
    DEFAULT_MASK_CHAR,
    DEFAULT_REVEAL_CHARS,
    MIN_LENGTH_FOR_PARTIAL,
)


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

def test_mask_value_empty_string_returns_empty():
    assert mask_value("") == ""


def test_mask_value_short_string_fully_masked():
    # Strings shorter than MIN_LENGTH_FOR_PARTIAL are fully masked.
    short = "abc"
    assert len(short) < MIN_LENGTH_FOR_PARTIAL
    result = mask_value(short)
    assert result == DEFAULT_MASK_CHAR * len(short)


def test_mask_value_long_string_reveals_suffix():
    value = "supersecret"  # 11 chars >= MIN_LENGTH_FOR_PARTIAL
    result = mask_value(value)
    assert result.endswith(value[-DEFAULT_REVEAL_CHARS:])
    assert result.startswith(DEFAULT_MASK_CHAR * (len(value) - DEFAULT_REVEAL_CHARS))


def test_mask_value_full_flag_masks_everything():
    value = "supersecret"
    result = mask_value(value, full=True)
    assert result == DEFAULT_MASK_CHAR * len(value)


def test_mask_value_custom_reveal_chars():
    value = "abcdefghij"  # 10 chars
    result = mask_value(value, reveal_chars=2)
    assert result == "********ij"


def test_mask_value_custom_mask_char():
    value = "supersecret"
    result = mask_value(value, mask_char="#")
    assert "#" in result
    assert "*" not in result


def test_mask_value_length_preserved():
    for val in ["x", "hello", "averylongsecretvalue"]:
        assert len(mask_value(val)) == len(val)


# ---------------------------------------------------------------------------
# mask_dict
# ---------------------------------------------------------------------------

def test_mask_dict_returns_all_keys():
    data = {"KEY1": "value1", "KEY2": "value2"}
    result = mask_dict(data)
    assert set(result.keys()) == set(data.keys())


def test_mask_dict_values_are_masked():
    data = {"SECRET": "supersecretvalue"}
    result = mask_dict(data)
    assert result["SECRET"] != data["SECRET"]


def test_mask_dict_empty():
    assert mask_dict({}) == {}


# ---------------------------------------------------------------------------
# format_masked_table
# ---------------------------------------------------------------------------

def test_format_masked_table_empty_returns_placeholder():
    assert format_masked_table({}) == "(empty)"


def test_format_masked_table_contains_keys():
    data = {"API_KEY": "supersecretvalue", "DB_PASS": "anotherpassword1"}
    output = format_masked_table(data)
    for key in data:
        assert key in output


def test_format_masked_table_does_not_contain_plain_values():
    data = {"API_KEY": "supersecretvalue"}
    output = format_masked_table(data)
    assert "supersecretvalue" not in output


def test_format_masked_table_sorted_output():
    data = {"ZEBRA": "aaaaaaaaaaaa", "ALPHA": "bbbbbbbbbbbb"}
    lines = format_masked_table(data).splitlines()
    assert lines[0].startswith("ALPHA")
    assert lines[1].startswith("ZEBRA")
