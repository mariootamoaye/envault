import os
import pytest
from click.testing import CliRunner
from envault.cli_diff import cmd_diff
from envault.store import VaultStore


@pytest.fixture
def runner():
    return CliRunner()


def _make_store(tmp_path, name, password, variables):
    path = tmp_path / name
    store = VaultStore(str(path))
    for k, v in variables.items():
        store.set(k, v, password)
    store.save()
    return store


def test_diff_dotenv_added_removed(tmp_path, runner):
    store = _make_store(tmp_path, "vault.json", "pw", {"FOO": "bar", "OLD": "gone"})
    dotenv = tmp_path / ".env"
    dotenv.write_text("FOO=bar\nNEW=here\n")

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cmd_diff,
            ["dotenv", str(dotenv)],
            input="pw\n",
            catch_exceptions=False,
            env={"ENVAULT_VAULT_PATH": str(tmp_path / "vault.json")},
        )
    assert result.exit_code == 0
    assert "+ NEW" in result.output
    assert "- OLD" in result.output


def test_diff_dotenv_unchanged(tmp_path, runner):
    store = _make_store(tmp_path, "vault.json", "pw", {"FOO": "bar"})
    dotenv = tmp_path / ".env"
    dotenv.write_text("FOO=bar\n")

    result = runner.invoke(
        cmd_diff,
        ["dotenv", str(dotenv)],
        input="pw\n",
        catch_exceptions=False,
        env={"ENVAULT_VAULT_PATH": str(tmp_path / "vault.json")},
    )
    assert result.exit_code == 0
    assert "  FOO" in result.output


def test_diff_dotenv_show_values(tmp_path, runner):
    store = _make_store(tmp_path, "vault.json", "pw", {"FOO": "bar"})
    dotenv = tmp_path / ".env"
    dotenv.write_text("FOO=baz\n")

    result = runner.invoke(
        cmd_diff,
        ["dotenv", str(dotenv), "--show-values"],
        input="pw\n",
        catch_exceptions=False,
        env={"ENVAULT_VAULT_PATH": str(tmp_path / "vault.json")},
    )
    assert result.exit_code == 0
    assert "'bar'" in result.output
    assert "'baz'" in result.output
