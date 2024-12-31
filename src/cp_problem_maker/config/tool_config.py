from pathlib import Path
from typing import Literal, Optional, Self

import pydantic
from pydantic import BaseModel, ConfigDict, Field

from cp_problem_maker import anchor
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.utils import _pydantic

logger = get_logger(__name__)

# ==== Checker ====


_CheckerStyle = Literal["testlib", "yukicoder"]


class _ExitCodeConfig(BaseModel):
    """Exit code configuration for the checker.

    Default settings are based on testlib.
    See https://github.com/MikeMirzayanov/testlib/blob/master/testlib.h
    for more details.
    """

    AC: int = Field(0, description="Exit code for accepted")
    WA: int = Field(1, description="Exit code for wrong answer")
    PE: int = Field(2, description="Exit code for presentation error")
    FAIL: int = Field(3, description="Exit code for fail")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )

    @pydantic.model_validator(mode="after")
    def _validate_exit_codes(self) -> Self:
        values = self.model_dump()
        if len(set(values.values())) != len(values):
            raise ValueError("Exit codes must be unique")
        return self


class _Checker(BaseModel):
    style: _CheckerStyle = Field("testlib", description="Default style of checker")

    exit_code: _ExitCodeConfig = Field(
        default_factory=_ExitCodeConfig,
        description="Exit code configuration for the checker",
    )

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


# ==== Language ====


_DefaultLanguage = Literal["C++", "Python"]


class _CppDefault(BaseModel):
    compiler: str = Field("g++", description="Compiler command")
    flags: list[str] = Field(
        [
            "-std=c++20",
            "-Wall",
            "-Wextra",
            "-fsplit-stack",
            "-g",
            "-fsanitize=address",
        ],
        description="Compiler flags",
    )

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


class _CppOverride(BaseModel):
    compiler: Optional[str] = Field(None, description="Override compiler command")
    flags: Optional[list[str]] = Field(None, description="Override compiler flags.")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


class _Cpp(_CppDefault):
    solver: Optional[_CppOverride] = Field(
        _CppOverride(
            flags=[
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-fsplit-stack",
                "-O2",
            ]
        ),
        description="Override configuration for the solver",
    )

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


class _Python(BaseModel):
    python: str = Field("python", description="Python executable")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


class _Language(BaseModel):
    default: _DefaultLanguage = Field("C++", description="Default language")

    cpp: _Cpp = Field(default_factory=_Cpp, description="Configuration for C++")
    python: _Python = Field(
        default_factory=_Python, description="Configuration for Python"
    )

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


# ==== Path ====


class _Path(BaseModel):
    problem_config: str = Field(
        "problem.toml", description="Path to the problem configuration file"
    )
    inputs: str = Field("test/in/", description="Directory to store inputs")
    outputs: str = Field("test/out/", description="Directory to store outputs")
    solutions: str = Field("src/sol/", description="Directory to store solutions")
    generators: str = Field("src/gen/", description="Directory to store generators")
    checker: str = Field(
        "src/checker",
        description="Path to the checker source file (without extension)",
    )
    verifier: str = Field(
        "src/verifier",
        description="Path to the checker source file (without extension)",
    )
    params: str = Field("src/params", description="Path to the parameters file")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


# ==== Config ====


class _Config(BaseModel):
    checker: _Checker = Field(
        default_factory=_Checker, description="Configuration for the checker"
    )
    language: _Language = Field(
        default_factory=_Language, description="Configuration for the language"
    )
    path: _Path = Field(
        default_factory=_Path, description="Configuration for the directories"
    )

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


# ==== Public ====

DEFAULT_CONFIG_PATH = anchor.SOURCE_ROOT / "data/default_config.toml"
GLOBAL_CONFIG_PATH = anchor.SOURCE_ROOT / "data/global_config.toml"


def load_default_config() -> _Config:
    logger.info("Loading default configuration")
    config = _pydantic.load_model(_Config, DEFAULT_CONFIG_PATH, strict=True)
    logger.debug("Default configuration: %s", config.model_dump(mode="json"))
    return config


def load_global_config() -> _Config:
    logger.info("Loading global configuration")
    config = _pydantic.load_model(_Config, GLOBAL_CONFIG_PATH, strict=True)
    logger.debug("Global configuration: %s", config.model_dump(mode="json"))
    return config


def load_local_config(local_config_path: Path) -> _Config:
    logger.info("Loading local configuration")
    config = load_global_config()
    if local_config_path.exists():
        update_dict = _pydantic.read_file_as_dict(local_config_path)
        _pydantic.update_model(config, update_dict)
    logger.debug("Local configuration: %s", config.model_dump(mode="json"))
    return config
