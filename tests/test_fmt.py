"""Tests for envault.fmt."""

import pytest
from envault.fmt import (
    infer_type,
    truncate,
    format_row,
    format_table,
    format_pairs,
)


# --- infer_type ---

def test_infer_type_bool_true():
    assert infer_type("true") == "bool"
    assert infer_type("yes") == "bool"
    assert infer_type("1") == "bool"


def test_infer_type_bool_false():
    assert infer_type("false") == "bool"
    assert infer_type("no") == "bool"
    assert infer_type("0") == "bool"


def test_infer_type_int():
    assert infer_type("42") == "int"
    assert infer_type("-7") == "int"


def test_infer_type_float():
    assert infer_type("3.14") == "float"
    assert infer_type("-0.5") == "float"


def test_infer_type_url():
    assert infer_type("https://example.com") == "url"
    assert infer_type("http://localhost:8080") == "url"


def test_infer_type_str():
    assert infer_type("hello world") == "str"
    assert infer_type("") == "str"


# --- truncate ---

def test_truncate_short_string_unchanged():
    assert truncate("hello", max_len=40) == "hello"


def test_truncate_exact_length_unchanged():
    s = "a" * 40
    assert truncate(s, max_len=40) == s


def test_truncate_long_string_cut():
    s = "a" * 50
    result = truncate(s, max_len=40)
    assert result.endswith("...")
    assert len(result) == 40


def test_truncate_custom_placeholder():
    result = truncate("abcdefghij", max_len=6, placeholder="--")
    assert result == "abcd--"
    assert len(result) == 6


# --- format_row ---

def test_format_row_contains_key_and_value():
    row = format_row("MY_KEY", "my_value")
    assert "MY_KEY" in row
    assert "my_value" in row


def test_format_row_with_type_shows_type_label():
    row = format_row("PORT", "8080", show_type=True)
    assert "int" in row


# --- format_table ---

def test_format_table_empty_returns_empty_label():
    assert format_table({}) == "(empty)"


def test_format_table_contains_all_keys():
    data = {"FOO": "bar", "BAZ": "qux"}
    table = format_table(data)
    assert "FOO" in table
    assert "BAZ" in table


def test_format_table_sorted_keys():
    data = {"Z_KEY": "1", "A_KEY": "2"}
    lines = format_table(data).splitlines()
    assert "A_KEY" in lines[0]


def test_format_table_with_type_has_header():
    table = format_table({"HOST": "localhost"}, show_type=True)
    assert "KEY" in table
    assert "TYPE" in table


# --- format_pairs ---

def test_format_pairs_returns_tuples():
    pairs = format_pairs({"X": "hello"})
    assert len(pairs) == 1
    key, val, typ = pairs[0]
    assert key == "X"
    assert val == "hello"
    assert typ == "str"


def test_format_pairs_sorted():
    pairs = format_pairs({"Z": "1", "A": "2"})
    assert pairs[0][0] == "A"
    assert pairs[1][0] == "Z"
