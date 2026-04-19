import pytest
from envault.template import (
    find_variables,
    render_template,
    render_file,
    check_template,
    RenderError,
)


def test_find_variables_empty():
    assert find_variables("no placeholders here") == []


def test_find_variables_single():
    assert find_variables("hello ${NAME}") == ["NAME"]


def test_find_variables_multiple():
    result = find_variables("${A} and ${B} and ${A}")
    assert result == ["A", "B", "A"]


def test_render_simple_substitution():
    out = render_template("Hello, ${NAME}!", {"NAME": "world"})
    assert out == "Hello, world!"


def test_render_multiple_vars():
    out = render_template("${HOST}:${PORT}", {"HOST": "localhost", "PORT": "5432"})
    assert out == "localhost:5432"


def test_render_strict_raises_on_missing():
    with pytest.raises(RenderError, match="Missing variables: FOO"):
        render_template("${FOO}", {}, strict=True)


def test_render_non_strict_leaves_placeholder():
    out = render_template("${FOO}", {}, strict=False)
    assert out == "${FOO}"


def test_render_partial_missing_strict():
    with pytest.raises(RenderError):
        render_template("${A} ${B}", {"A": "1"}, strict=True)


def test_check_template_all_ok():
    result = check_template("${A}", {"A": "1"})
    assert result == [("A", "ok")]


def test_check_template_missing():
    result = check_template("${A} ${B}", {"A": "1"})
    assert ("A", "ok") in result
    assert ("B", "missing") in result


def test_render_file(tmp_path):
    tpl = tmp_path / "config.tpl"
    tpl.write_text("DB=${DB_URL}\nSECRET=${SECRET}")
    out = render_file(str(tpl), {"DB_URL": "postgres://localhost", "SECRET": "abc"})
    assert out == "DB=postgres://localhost\nSECRET=abc"
