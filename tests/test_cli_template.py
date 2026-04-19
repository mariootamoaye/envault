import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli_template import cmd_template


@pytest.fixture
def runner():
    return CliRunner()


def _make_store(data: dict):
    store = MagicMock()
    store.keys.return_value = list(data.keys())
    store.get.side_effect = lambda k: data[k]
    return store


def test_render_to_stdout(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("Hello, ${NAME}!")
    store = _make_store({"NAME": "Alice"})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["render", str(tpl)])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output


def test_render_to_file(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("${A}")
    out = tmp_path / "out.txt"
    store = _make_store({"A": "42"})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["render", str(tpl), "-o", str(out)])
    assert result.exit_code == 0
    assert out.read_text() == "42"


def test_render_strict_missing_fails(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("${MISSING_VAR}")
    store = _make_store({})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["render", str(tpl)])
    assert result.exit_code != 0
    assert "Missing" in result.output


def test_render_non_strict_leaves_placeholder(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("${GHOST}")
    store = _make_store({})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["render", str(tpl), "--non-strict"])
    assert result.exit_code == 0
    assert "${GHOST}" in result.output


def test_check_all_present(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("${FOO} ${BAR}")
    store = _make_store({"FOO": "1", "BAR": "2"})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["check", str(tpl)])
    assert result.exit_code == 0
    assert "✓" in result.output


def test_check_missing_exits_nonzero(runner, tmp_path):
    tpl = tmp_path / "t.tpl"
    tpl.write_text("${MISSING}")
    store = _make_store({})
    with patch("envault.cli_template._get_store", return_value=store), \
         patch("envault.cli_template._prompt_password", return_value="pw"):
        result = runner.invoke(cmd_template, ["check", str(tpl)])
    assert result.exit_code != 0
    assert "✗" in result.output
