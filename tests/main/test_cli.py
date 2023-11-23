from typer.testing import CliRunner

from pyprojectviz.__main__ import app

runner = CliRunner()


def test_app_success():
    result = runner.invoke(
        app,
        [
            ".",
            "--output",
            "test",
        ],
    )
    assert result.exit_code == 0
    assert "Graph generated at" in result.stdout


def test_app_success_with_config():
    result = runner.invoke(
        app,
        [
            ".",
            "--output",
            "test",
            "--config",
            "examples/example_conf_file.yaml",
        ],
    )
    assert result.exit_code == 0
    assert "Graph generated at" in result.stdout


def test_app_fail():
    result = runner.invoke(app, ["invalid_path", "--output", "test"])
    assert result.exit_code == 1
    assert "Invalid path to project" in result.stdout


def test_app_config_fail():
    result = runner.invoke(
        app, [".", "--output", "test", "--config", "invalid_config"]
    )
    assert result.exit_code == 1
    assert "Invalid path to configuration file" in result.stdout
