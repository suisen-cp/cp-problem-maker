import argparse
from logging import Logger, getLogger
from pathlib import Path
import tempfile
from typing import List

from cp_problem_maker.problem import Problem
from cp_problem_maker.config import Config
from cp_problem_maker.compile import compile_solution, compile_checker, CompileConfig
from cp_problem_maker.testcase import TestCase
from cp_problem_maker.judge import UnexpectedAccepted, assert_judge_status, JudgeStatus, judge


logger: Logger = getLogger(__name__)


def add_parser(subparsers):
    parser_check: argparse.ArgumentParser = subparsers.add_parser(
        "check", description="check solutions")
    parser_check.add_argument(
        "-p", "--path",
        type=str,
        default="."
    )
    parser_check.add_argument(
        "-s", "--solutions",
        type=str,
        nargs="*"
    )


def run(path: Path, solutions: List[str]):
    problem = Problem(path)
    compile_config = CompileConfig(problem.compile_config_file)
    config = Config(problem.config_file)

    compile_checker(problem.checker_file, compile_config=compile_config)

    if not solutions:
        solutions = list(
            solution_config.name for solution_config in config.solution_config.values())

    for solution in solutions:
        if solution not in config.solution_config:
            logger.error(
                f'Configuration about the solution "{solution}" is missing. skipped.'
            )
            continue
        logger.info(f'started checking the solution "{solution}"')

        solution_config = config.solution_config[solution]

        name = solution_config.name
        solution_file = problem.solutions_folder / name
        compile_solution(solution_file, compile_config=compile_config)

        detect_tle = False
        detect_re = False
        detect_wa = False

        for testcase_config in config.testcase_config.values():
            name = testcase_config.name
            number = testcase_config.number
            for case_no in range(number):
                generator_file = problem.gen_folder / Path(name)
                testcase = TestCase(generator_file, case_no)
                input_file = problem.in_folder / testcase.input_file_name
                output_file_expected = problem.out_folder / testcase.output_file_name

                with tempfile.NamedTemporaryFile(mode='w') as output_file_actual_wrapper:
                    output_file_actual = Path(output_file_actual_wrapper.name)
                    logger.info("checking solution...")
                    result = judge(
                        input_file=input_file,
                        output_file=output_file_actual,
                        solution_file=solution_file,
                        checker_file=problem.checker_file,
                        output_file_expected=output_file_expected,
                        config=config,
                        parents=True,
                        exist_ok=True
                    )
                    logger.info(f"  result  : {result.status}")
                    logger.info(f"  time    : {result.elapsed_ms} ms")
                    assert_judge_status(result.status, solution_config)

                    detect_tle |= result.status == JudgeStatus.TLE
                    detect_re |= result.status == JudgeStatus.RE
                    detect_wa |= result.status == JudgeStatus.WA

        if solution_config.allow_tle and not detect_tle:
            logger.warning(
                f'"allow_tle" flag is set to the solution "{solution_config.name}", but there is no TLE cases.'
            )
        if solution_config.allow_re and not detect_re:
            logger.warning(
                f'"allow_re" flag is set to the solution "{solution_config.name}", but there is no RE cases.'
            )
        if solution_config.wrong and not detect_wa:
            logger.error(
                f'"wrong" flag is set to the solution "{solution_config.name}", but there is no WA cases.'
            )
            raise UnexpectedAccepted()