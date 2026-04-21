"""Tests for envault.cascade."""

from __future__ import annotations

import pytest

from envault.cascade import cascade, cascade_with_sources, format_cascade
from envault.store import VaultStore
from envault.profile import vault_path_for_profile


PASSWORD = "test-secret"


def _populate(tmp_path, monkeypatch, profile: str, data: dict) -> None:
    """Write *data* into a profile vault inside *tmp_path*."""
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    path = vault_path_for_profile(profile)
    store = VaultStore(path, PASSWORD)
    for k, v in data.items():
        store.set(k, v)
    store.save()


@pytest.fixture(autouse=True)
def _set_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))


def test_cascade_single_profile(tmp_path, monkeypatch):
    _populate(tmp_path, monkeypatch, "base", {"A": "1", "B": "2"})
    result = cascade(["base"], PASSWORD)
    assert result == {"A": "1", "B": "2"}


def test_cascade_later_profile_overrides(tmp_path, monkeypatch):
    _populate(tmp_path, monkeypatch, "base", {"A": "base", "B": "base"})
    _populate(tmp_path, monkeypatch, "prod", {"B": "prod", "C": "prod"})
    result = cascade(["base", "prod"], PASSWORD)
    assert result["A"] == "base"
    assert result["B"] == "prod"   # overridden
    assert result["C"] == "prod"


def test_cascade_empty_profile_is_skipped(tmp_path, monkeypatch):
    _populate(tmp_path, monkeypatch, "base", {"X": "hello"})
    _populate(tmp_path, monkeypatch, "empty", {})
    result = cascade(["base", "empty"], PASSWORD)
    assert result == {"X": "hello"}


def test_cascade_with_sources_tracks_origin(tmp_path, monkeypatch):
    _populate(tmp_path, monkeypatch, "base", {"A": "1", "B": "base"})
    _populate(tmp_path, monkeypatch, "override", {"B": "new"})
    result = cascade_with_sources(["base", "override"], PASSWORD)
    assert result["A"] == ("1", "base")
    assert result["B"] == ("new", "override")


def test_cascade_with_sources_empty_returns_empty(tmp_path, monkeypatch):
    _populate(tmp_path, monkeypatch, "empty", {})
    result = cascade_with_sources(["empty"], PASSWORD)
    assert result == {}


def test_format_cascade_empty():
    assert format_cascade({}) == "(no variables)"


def test_format_cascade_contains_key_value_source():
    sourced = {"DB_URL": ("postgres://localhost", "prod")}
    output = format_cascade(sourced)
    assert "DB_URL" in output
    assert "postgres://localhost" in output
    assert "[prod]" in output


def test_format_cascade_sorted_keys():
    sourced = {"Z": ("z", "p"), "A": ("a", "p")}
    lines = format_cascade(sourced).splitlines()
    assert lines[0].startswith("A=")
    assert lines[1].startswith("Z=")
