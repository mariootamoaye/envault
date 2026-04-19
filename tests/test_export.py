"""Tests for envault.export module."""
import pytest
from envault.export import render, export_dotenv, export_bash, export_fish


SAMPLE = {"DB_URL": "postgres://localhost/db", "API_KEY": "s3cr3t"}


def test_dotenv_format_contains_keys():
    out = export_dotenv(SAMPLE)
    assert "DB_URL=" in out
    assert "API_KEY=" in out


def test_dotenv_format_quoted_values():
    out = export_dotenv({"KEY": "hello world"})
    assert "KEY='hello world'" in out


def test_dotenv_single_quote_escaping():
    out = export_dotenv({"KEY": "it's fine"})
    assert "KEY='it'\\''s fine'" in out


def test_bash_format_has_export():
    out = export_bash(SAMPLE)
    assert out.startswith("export ") or "export API_KEY=" in out
    assert "export DB_URL=" in out


def test_fish_format_has_set():
    out = export_fish(SAMPLE)
    assert "set -x API_KEY" in out
    assert "set -x DB_URL" in out


def test_render_dispatches_dotenv():
    out = render(SAMPLE, "dotenv")
    assert "API_KEY=" in out


def test_render_dispatches_bash():
    out = render(SAMPLE, "bash")
    assert "export API_KEY=" in out


def test_render_dispatches_fish():
    out = render(SAMPLE, "fish")
    assert "set -x API_KEY" in out


def test_render_unknown_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        render(SAMPLE, "powershell")


def test_empty_secrets_returns_empty_string():
    assert export_dotenv({}) == ""
    assert export_bash({}) == ""
    assert export_fish({}) == ""


def test_output_is_sorted():
    secrets = {"ZEBRA": "1", "ALPHA": "2", "MIDDLE": "3"}
    lines = export_dotenv(secrets).strip().splitlines()
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)
