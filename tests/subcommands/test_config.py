from pathlib import Path
from typing import Literal

import pydantic_core
import pytest
import toml

from cp_problem_maker import subcommands
from cp_problem_maker.config import tool_config
from cp_problem_maker.project.problem import ProblemWithConfig


@pytest.mark.parametrize("value", ["C++", "Python"])
def test_update_local_config(
    monkeypatch: pytest.MonkeyPatch,
    project_root: Path,
    value: str,
) -> None:
    monkeypatch.chdir(project_root)
    subcommands.ConfigCommand.config("local", ["language", "default"], value)
    problem = ProblemWithConfig(project_root, search_root=False)
    local_config = problem.config
    global_config = tool_config.load_global_config()
    # Check if the settings are correctly reflected
    assert local_config.language.default == value
    if value != tool_config._Language.model_fields["default"].default:
        assert global_config.language.default != value
    # Check if the new settings are correctly written to the local config file
    assert toml.load(problem.problem.local_config_file)["language"]["default"] == value


@pytest.mark.parametrize("value", ["C++", "Python"])
def test_update_global_config(
    monkeypatch: pytest.MonkeyPatch,
    project_root: Path,
    value: str,
) -> None:
    monkeypatch.chdir(project_root)
    tmp_global_config_path = Path("tmp_global_config.toml")
    tmp_global_config_path.touch()
    monkeypatch.setattr(
        "cp_problem_maker.subcommands.ConfigCommand.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    monkeypatch.setattr(
        "cp_problem_maker.config.tool_config.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    subcommands.ConfigCommand.config("global", ["language", "default"], value)
    local_config = ProblemWithConfig(project_root, search_root=False).config
    global_config = tool_config.load_global_config()
    # Check if the settings are correctly reflected
    assert local_config.language.default == value
    assert global_config.language.default == value
    # Check if the new settings are correctly written to the local config file
    assert toml.load(tmp_global_config_path)["language"]["default"] == value


def test_update_both_config(
    monkeypatch: pytest.MonkeyPatch, project_root: Path
) -> None:
    monkeypatch.chdir(project_root)
    tmp_global_config_path = Path("tmp_global_config.toml")
    tmp_global_config_path.touch()
    monkeypatch.setattr(
        "cp_problem_maker.subcommands.ConfigCommand.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    monkeypatch.setattr(
        "cp_problem_maker.config.tool_config.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    subcommands.ConfigCommand.config("local", ["language", "default"], "C++")
    subcommands.ConfigCommand.config("global", ["language", "default"], "Python")
    problem = ProblemWithConfig(project_root, search_root=False)
    local_config = problem.config
    global_config = tool_config.load_global_config()
    # Check if the settings are correctly reflected
    assert local_config.language.default == "C++"
    assert global_config.language.default == "Python"
    # Check if the new settings are correctly written to the local config file
    assert toml.load(problem.problem.local_config_file)["language"]["default"] == "C++"
    assert toml.load(tmp_global_config_path)["language"]["default"] == "Python"


@pytest.mark.parametrize("scope", ["global", "local"])
def test_config_invalid_key(
    monkeypatch: pytest.MonkeyPatch,
    project_root: Path,
    scope: Literal["global", "local"],
) -> None:
    monkeypatch.chdir(project_root)
    tmp_global_config_path = Path("tmp_global_config.toml")
    tmp_global_config_path.touch()
    monkeypatch.setattr(
        "cp_problem_maker.subcommands.ConfigCommand.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    with pytest.raises(AttributeError):
        subcommands.ConfigCommand.config(scope, ["Invalid Key"], "Hoge")


@pytest.mark.parametrize("scope", ["global", "local"])
def test_config_invalid_value(
    monkeypatch: pytest.MonkeyPatch,
    project_root: Path,
    scope: Literal["global", "local"],
) -> None:
    monkeypatch.chdir(project_root)
    tmp_global_config_path = Path("tmp_global_config.toml")
    tmp_global_config_path.touch()
    monkeypatch.setattr(
        "cp_problem_maker.subcommands.ConfigCommand.GLOBAL_CONFIG_PATH",
        tmp_global_config_path,
    )
    with pytest.raises(pydantic_core.ValidationError):
        subcommands.ConfigCommand.config(scope, ["language", "default"], 1)
