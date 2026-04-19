import pytest
from envault.diff import diff_dicts, format_diff, DiffEntry


@pytest.fixture
def left():
    return {"FOO": "bar", "SHARED": "same", "OLD": "gone"}


@pytest.fixture
def right():
    return {"FOO": "baz", "SHARED": "same", "NEW": "here"}


def test_diff_detects_added(left, right):
    entries = diff_dicts(left, right)
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "NEW"


def test_diff_detects_removed(left, right):
    entries = diff_dicts(left, right)
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "OLD"


def test_diff_detects_changed(left, right):
    entries = diff_dicts(left, right)
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "FOO"
    assert changed[0].left == "bar"
    assert changed[0].right == "baz"


def test_diff_detects_unchanged(left, right):
    entries = diff_dicts(left, right)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "SHARED"


def test_diff_empty_dicts():
    assert diff_dicts({}, {}) == []


def test_diff_identical_dicts():
    d = {"A": "1", "B": "2"}
    entries = diff_dicts(d, d)
    assert all(e.status == "unchanged" for e in entries)


def test_format_diff_symbols(left, right):
    entries = diff_dicts(left, right)
    output = format_diff(entries)
    assert "+ NEW" in output
    assert "- OLD" in output
    assert "~ FOO" in output
    assert "  SHARED" in output


def test_format_diff_with_values(left, right):
    entries = diff_dicts(left, right)
    output = format_diff(entries, show_values=True)
    assert "'bar'" in output
    assert "'baz'" in output
