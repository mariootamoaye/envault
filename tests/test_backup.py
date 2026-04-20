"""Tests for envault.backup module."""

import gzip
import json
import pytest
from pathlib import Path

from envault.backup import (
    backup_vault,
    restore_vault,
    list_backups,
    delete_backup,
)


@pytest.fixture()
def vault_file(tmp_path):
    vf = tmp_path / "vault.json"
    vf.write_text(json.dumps({"FOO": "bar", "BAZ": "qux"}))
    return vf


@pytest.fixture()
def backup_dir(tmp_path):
    return tmp_path / "backups"


def test_backup_creates_gz_file(vault_file, backup_dir):
    dest = backup_vault(vault_file, backup_dir)
    assert dest.exists()
    assert dest.suffix == ".gz"


def test_backup_content_is_valid_json(vault_file, backup_dir):
    dest = backup_vault(vault_file, backup_dir)
    with gzip.open(dest, "rb") as fh:
        data = json.loads(fh.read())
    assert data["FOO"] == "bar"


def test_backup_missing_vault_raises(backup_dir, tmp_path):
    missing = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        backup_vault(missing, backup_dir)


def test_restore_overwrites_vault(vault_file, backup_dir, tmp_path):
    dest = backup_vault(vault_file, backup_dir)
    target = tmp_path / "restored.json"
    restore_vault(dest, target)
    data = json.loads(target.read_text())
    assert data["BAZ"] == "qux"


def test_restore_missing_backup_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_vault(tmp_path / "ghost.json.gz", tmp_path / "vault.json")


def test_restore_invalid_json_raises(tmp_path):
    bad = tmp_path / "bad.json.gz"
    with gzip.open(bad, "wb") as fh:
        fh.write(b"not json!!!")
    with pytest.raises(ValueError, match="invalid JSON"):
        restore_vault(bad, tmp_path / "vault.json")


def test_list_backups_sorted_newest_first(vault_file, backup_dir):
    b1 = backup_vault(vault_file, backup_dir)
    b2 = backup_vault(vault_file, backup_dir)
    results = list_backups(backup_dir)
    assert len(results) == 2
    assert results[0].name >= results[1].name


def test_list_backups_empty_when_no_dir(tmp_path):
    assert list_backups(tmp_path / "nodir") == []


def test_delete_backup_removes_file(vault_file, backup_dir):
    dest = backup_vault(vault_file, backup_dir)
    delete_backup(dest)
    assert not dest.exists()


def test_delete_backup_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_backup(tmp_path / "ghost.json.gz")
