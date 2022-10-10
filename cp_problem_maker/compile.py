import logging
from pathlib import Path
from subprocess import check_call
from typing import List

from cp_problem_maker.problem import Problem
from cp_problem_maker.config import Config
from cp_problem_maker.testcase import GeneratorType
from cp_problem_maker.util import pathlib_util

logger: logging.Logger = logging.getLogger(__name__)

def _logging_compile_info(file_name: str, role_name: str) -> None:
    logger.info(f'compiling {role_name.ljust(10)}  : {file_name}...')

def _compile_cmd(cpp_source_file: Path) -> List[str]:
    cpp_exe_file = cpp_source_file.with_suffix('')
    cmd = [
        "g++",
        "-std=gnu++17",
        "-fsplit-stack",
        "-Wall",
        "-Wextra",
        "-O2",
        f"{cpp_source_file}",
        "-o",
        f"{cpp_exe_file}"
    ]
    return cmd

def _compile(cpp_source_file: Path, role_name: str) -> None:
    pathlib_util.ensure_file(cpp_source_file)
    _logging_compile_info(cpp_source_file.name, role_name)
    check_call(_compile_cmd(cpp_source_file))

def compile_checker(checker_file: Path) -> None:
    _compile(checker_file, "checker")

def compile_verifier(verifier_file: Path) -> None:
    _compile(verifier_file, "verifier")

def compile_generator(gen_file: Path) -> None:
    _compile(gen_file, "generator")

def compile_solution(solution_file: Path) -> None:
    _compile(solution_file, "solution")

def compile_all(problem: Problem) -> None:
    compile_verifier(problem.verifier_file)
    compile_checker(problem.checker_file)

    config = Config(problem.config_file)
    for testcase_config in config.testcase_config.values():
        generator_file = problem.gen_folder / testcase_config.name
        generator_type = GeneratorType.from_file(generator_file)
        if generator_type == GeneratorType.CPP:
            compile_generator(generator_file)

    for solution_config in config.solution_config.values():
        solution_file = problem.solutions_folder / solution_config.name
        compile_solution(solution_file)
