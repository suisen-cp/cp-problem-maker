from pathlib import Path

from pytest_mock import MockerFixture

from cp_problem_maker.config.tool_config import (
    _Config,
    load_default_config,
    load_global_config,
    load_local_config,
)
from tests.helpers.files import temp_files


def test_default_config_consistency() -> None:
    file_config = load_default_config()
    defaulgt_constructed_config = _Config()
    assert file_config == defaulgt_constructed_config


def test_global_config(mocker: MockerFixture) -> None:
    global_config = """
[checker]
style = "yukicoder"
[language]
default = "Python"
"""
    with temp_files(1, suffix=".toml") as (temp_config,):
        temp_config.write(global_config)
        temp_config.seek(0)
        mocker.patch(
            "cp_problem_maker.config.tool_config.GLOBAL_CONFIG_PATH",
            Path(temp_config.name),
        )
        config = load_global_config()
        assert config.language.default == "Python"
        assert config.checker.style == "yukicoder"


def test_local_config() -> None:
    local_config = """
[path]
problem_config = "AAAAA.toml"
"""
    with temp_files(1, suffix=".toml") as (temp_config,):
        temp_config.write(local_config)
        temp_config.seek(0)
        config = load_local_config(Path(temp_config.name))
        assert config.path.problem_config == "AAAAA.toml"


def test_local_config_with_global_config(mocker: MockerFixture) -> None:
    global_config = """
[checker]
style = "yukicoder"
[language]
default = "Python"
"""

    local_config = """
[path]
problem_config = "AAAAA.toml"
"""
    with temp_files(2, suffix=".toml") as (temp_global_config, temp_local_config):
        temp_global_config.write(global_config)
        temp_global_config.seek(0)
        mocker.patch(
            "cp_problem_maker.config.tool_config.GLOBAL_CONFIG_PATH",
            Path(temp_global_config.name),
        )
        temp_local_config.write(local_config)
        temp_local_config.seek(0)
        config = load_local_config(Path(temp_local_config.name))
        assert config.language.default == "Python"
        assert config.checker.style == "yukicoder"
        assert config.path.problem_config == "AAAAA.toml"
