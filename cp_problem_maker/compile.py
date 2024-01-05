import logging
from pathlib import Path
from subprocess import check_call
from typing import Any, Dict, List
import toml

from cp_problem_maker.util import pathlib_util

logger: logging.Logger = logging.getLogger(__name__)

def _logging_compile_info(file_name: str, role_name: str) -> None:
    logger.info(f'compiling {role_name.ljust(10)}  : {file_name}...')


class CompileConfig:
    DEFAULT_COMPILER = 'g++'
    DEFAULT_FLAGS = [
        '-O2',
        '-Wall',
        '-Wextra',
    ]

    def __init__(self, config_file: Path) -> None:
        logger.info("loading configuration file for compilation...")
        pathlib_util.ensure_file(config_file)
        config: Dict[str, Any] = toml.load(config_file)
        self.compiler: str = config.get("compiler", CompileConfig.DEFAULT_COMPILER)
        self.flags: List[str] = config.get("flags", CompileConfig.DEFAULT_FLAGS)


def _compile_cmd(cpp_source_file: Path, compile_config: CompileConfig) -> List[str]:
    cpp_exe_file = cpp_source_file.with_suffix('')
    cmd = [
        f"{compile_config.compiler}",
    ]
    for flag in compile_config.flags:
        cmd.append(flag)
    cmd += [
        f"{cpp_source_file}",
        "-o",
        f"{cpp_exe_file}"
    ]
    return cmd

def _compile(cpp_source_file: Path, role_name: str, compile_config: CompileConfig) -> None:
    pathlib_util.ensure_file(cpp_source_file)
    _logging_compile_info(cpp_source_file.name, role_name)
    check_call(_compile_cmd(cpp_source_file, compile_config=compile_config))

def compile_checker(checker_file: Path, compile_config: CompileConfig) -> None:
    _compile(checker_file, "checker", compile_config=compile_config)

def compile_verifier(verifier_file: Path, compile_config: CompileConfig) -> None:
    _compile(verifier_file, "verifier", compile_config=compile_config)

def compile_generator(gen_file: Path, compile_config: CompileConfig) -> None:
    _compile(gen_file, "generator", compile_config=compile_config)

def compile_solution(solution_file: Path, compile_config: CompileConfig) -> None:
    _compile(solution_file, "solution", compile_config=compile_config)
