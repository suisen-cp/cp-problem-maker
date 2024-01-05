
from dataclasses import dataclass
import logging
from pathlib import Path
import textwrap
from typing import Any, Dict, List

from cp_problem_maker.util import pathlib_util

import toml

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class TestCaseConfig:
    name: str
    number: int

    @property
    def name_without_suffix(self):
        return str(Path(self.name).with_suffix(''))


@dataclass
class SolutionConfig:
    name: str
    allow_tle: bool
    allow_re: bool
    wrong: bool

    def __str__(self) -> str:
        return f'name = {self.name}, allow_tle = {self.allow_tle}, allow_re = {self.allow_re}, wrong = {self.wrong}'


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
        self.solution_config["correct.cpp"] = SolutionConfig(
            name="correct.cpp",
            allow_tle=False,
            allow_re=False,
            wrong=False
        )
        for solution_config in config.get("solutions", []):
            self.solution_config[solution_config["name"]] = SolutionConfig(
                name=solution_config["name"],
                allow_tle=solution_config.get("allow_tle", False),
                allow_re=solution_config.get("allow_re", False),
                wrong=solution_config.get("wrong", False)
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

        unavailable_parameter_type_error_message = textwrap.dedent(f"""
            Detected the unavailable type of parameter. You can use the types below:
            - integer / (nonempty) integer array
            - string  / (nonempty) string array
            - float   / (nonempty) float array
            - bool    / (nonempty) bool array
        """).strip()
    
        def cpp_value_str(x) -> str:
            # NOTE: isinstance(x, int) is True when x is bool
            if type(x) == int:
                return str(x)
            elif type(x) == str:
                return f'"{x}"'
            elif type(x) == float:
                return str(x)
            elif type(x) == bool:
                return 'true' if x else 'false'
            elif type(x) == list:
                return f"{{ {', '.join(map(cpp_value_str, x))} }}"
            raise ValueError(unavailable_parameter_type_error_message)
        
        def cpp_decl_str(x, name: str) -> str:
            if type(x) == int:
                return f'const long long {name}'
            elif type(x) == str:
                return f'const char* {name}'
            elif type(x) == float:
                return f'const long double {name}'
            elif type(x) == bool:
                return f'const bool {name}'
            elif type(x) == list and x and all(map(lambda e: isinstance(e, type(x[0])), value)):
                return f'{cpp_decl_str(x[0], name)}[{len(x)}]'

            raise ValueError(unavailable_parameter_type_error_message)

        for name, value in self.params.items():
            content.append(f'{cpp_decl_str(value, name)} = {cpp_value_str(value)};')
        if not exist_ok:
            pathlib_util.ensure_not_exists(params_file)
        params_file.touch()
        params_file.write_text('\n'.join(content))
