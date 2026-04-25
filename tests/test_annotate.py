"""Tests for envault.annotate."""

import pytest
from pathlib import Path
from envault.annotate import (
    load_annotations,
    set_annotation,
    remove_annotation,
    get_annotation,
    list_annotations,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.json"


def test_load_returns_empty_when_no_file(vault_path):
    assert load_annotations(vault_path) == {}


def test_set_annotation_creates_entry(vault_path):
    set_annotation(vault_path, "DB_URL", "Primary database connection string")
    ann = load_annotations(vault_path)
    assert ann["DB_URL"] == "Primary database connection string"


def test_set_annotation_overwrites_existing(vault_path):
    set_annotation(vault_path, "API_KEY", "old note")
    set_annotation(vault_path, "API_KEY", "new note")
    assert get_annotation(vault_path, "API_KEY") == "new note"


def test_set_annotation_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        set_annotation(vault_path, "", "some note")


def test_get_annotation_missing_key_returns_none(vault_path):
    assert get_annotation(vault_path, "MISSING") is None


def test_get_annotation_returns_note(vault_path):
    set_annotation(vault_path, "SECRET", "rotate monthly")
    assert get_annotation(vault_path, "SECRET") == "rotate monthly"


def test_remove_annotation_existing(vault_path):
    set_annotation(vault_path, "FOO", "bar")
    result = remove_annotation(vault_path, "FOO")
    assert result is True
    assert get_annotation(vault_path, "FOO") is None


def test_remove_annotation_missing_returns_false(vault_path):
    result = remove_annotation(vault_path, "NONEXISTENT")
    assert result is False


def test_list_annotations_multiple(vault_path):
    set_annotation(vault_path, "A", "note a")
    set_annotation(vault_path, "B", "note b")
    result = list_annotations(vault_path)
    assert result == {"A": "note a", "B": "note b"}


def test_annotations_persisted_to_disk(vault_path):
    set_annotation(vault_path, "PERSIST", "check disk")
    # reload from disk
    fresh = load_annotations(vault_path)
    assert fresh["PERSIST"] == "check disk"
