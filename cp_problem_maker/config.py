
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Dict, List

from cp_problem_maker.util import pathlib_util

import toml

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class TestCaseConfig:
    name: str
    number: int


@dataclass
class SolutionConfig:
    name: str
    allow_tle: bool
    wrong: bool

    def __str__(self) -> str:
        return f'name = {self.name}, allow_tle = {self.allow_tle}, wrong = {self.wrong}'


class Config:
    def __init__(self, config_file: Path) -> None:
        logger.info("loading configuration file...")
        pathlib_util.ensure_file(config_file)
        config: Dict[str, Any] = toml.load(config_file)
        self.title: str = str(config.get("title", "No Title"))
        self.timelimit: float = float(config.get("timelimit", 2.0))
        self.testcase_config: Dict[str, TestCaseConfig] = dict()
        for testcase_config in config.get("tests", []):
            self.testcase_config[testcase_config["name"]] = TestCaseConfig(
                name=testcase_config["name"],
                number=testcase_config["number"]
            )

        self.solution_config: Dict[str, SolutionConfig] = dict()
        for solution_config in config.get("solutions", []):
            self.solution_config[solution_config["name"]] = SolutionConfig(
                name=solution_config["name"],
                allow_tle=solution_config.get("allow_tle", False),
                wrong=solution_config.get("wrong", False)
            )
        self.solution_config["correct.cpp"] = SolutionConfig(
            name="correct.cpp", allow_tle=False, wrong=False
        )

        self.params: Dict[str, Any] = dict()
        for name, value in config.get("params", dict()).items():
            self.params[name] = value
    
    def write_params(self, params_file: Path, exist_ok=True) -> None:
        logger.info("writing params...")
        content: List[str] = [
            "#pragma once",
            "",
        ]
        for name, value in self.params.items():
            content.append(f"const long long {name} = {value};")
        if not exist_ok:
            pathlib_util.ensure_not_exists(params_file)
        params_file.touch()
        params_file.write_text('\n'.join(content))
