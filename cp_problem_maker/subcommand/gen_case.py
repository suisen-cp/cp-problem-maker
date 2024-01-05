import argparse
from logging import Logger, getLogger
from pathlib import Path
import shutil
from typing import Set

from cp_problem_maker.problem import Problem
from cp_problem_maker.config import Config
from cp_problem_maker.compile import compile_solution, compile_generator, compile_verifier, CompileConfig
from cp_problem_maker.testcase import GeneratorType, TestCase, SUFFIX_CPP, SUFFIX_HAND
from cp_problem_maker.subcommand import gen_params


logger: Logger = getLogger(__name__)


def add_parser(subparsers):
    parser_gen: argparse.ArgumentParser = subparsers.add_parser(
        "gen-case", description="generate testcases"
    )
    parser_gen.add_argument(
        "-p", "--path",
        type=str,
        default="."
    )
    parser_gen.add_argument(
        "--allow-replace",
        action="store_true"
    )


def run(path: Path, *, parents=False, exist_ok=False):
    gen_params.run(path, exist_ok=exist_ok)

    problem = Problem(path)

    compile_config = CompileConfig(problem.compile_config_file)
    config = Config(problem.config_file)

    compile_solution(problem.solution_file, compile_config=compile_config)
    compile_verifier(problem.verifier_file, compile_config=compile_config)

    unused_gen_files: Set[str] = set()
    unused_raw_input_files: Set[str] = set()
    for gen_file in problem.gen_folder.iterdir():
        if gen_file.is_file():
            if gen_file.suffix in SUFFIX_CPP:
                unused_gen_files.add(gen_file.name)
            if gen_file.suffix in SUFFIX_HAND:
                unused_raw_input_files.add(gen_file.stem)

    if exist_ok:
        logger.info(f"removing old inputs...")
        for f in problem.in_folder.iterdir():
            f_info = TestCase.get_testcase_info(f)
            
            is_generated_file = f_info is not None and f_info.is_input
            if not is_generated_file:
                f_type = "file" if f.is_file() else "folder"
                while True:
                    print(f'Is it ok to remove the {f_type} "{f.relative_to(problem.problem_folder)}"? [y/n]: ', end='', flush=True)
                    response = input().strip().lower()
                    if response in ['yes', 'y']:
                        if f.is_file():
                            f.unlink()
                        else:
                            shutil.rmtree(f)
                        break
                    elif response in ['no', 'n']:
                        break
            else:
                f.unlink()

        logger.info(f"removing old outputs...")
        for f in problem.out_folder.iterdir():
            f_info = TestCase.get_testcase_info(f)

            is_generated_file = f_info is not None and not f_info.is_input
            if not is_generated_file:
                f_type = "file" if f.is_file() else "folder"
                while True:
                    print(f'Is it ok to remove the {f_type} "{f.relative_to(problem.problem_folder)}"? [y/n]: ', end='', flush=True)
                    response = input().strip().lower()
                    if response in ['yes', 'y']:
                        if f.is_file():
                            f.unlink()
                        else:
                            shutil.rmtree(f)
                        break
                    elif response in ['no', 'n']:
                        break
            else:
                f.unlink()

    for testcase_config in config.testcase_config.values():
        name = testcase_config.name
        number = testcase_config.number
        generator_file = problem.gen_folder / Path(name)
        if GeneratorType.from_file(generator_file) == GeneratorType.CPP:
            compile_generator(generator_file, compile_config=compile_config)
        unused_gen_files.discard(name)
        for case_no in range(number):
            testcase = TestCase(generator_file, case_no)
            try:
                testcase.generate_input(
                    problem.in_folder,
                    parents=parents,
                    exist_ok=exist_ok
                )
                testcase.verify_input(
                    input_folder=problem.in_folder,
                    verifier_file=problem.verifier_file
                )
                testcase.generate_output(
                    input_folder=problem.in_folder,
                    output_folder=problem.out_folder,
                    solution_file=problem.solution_file,
                    config=config,
                    parents=parents,
                    exist_ok=exist_ok
                )
            except FileExistsError as e:
                logger.exception(e)
                logger.error(
                    "If you want to allow file replacement, give the '--allow-replace' flag."
                )
                exit(1)
            if testcase.generator_type == GeneratorType.RAW:
                unused_raw_input_files.discard(testcase.case_name_with_no)

    for unused_gen_file in unused_gen_files:
        logger.warning(
            f'The configuration for "{unused_gen_file}" is missing and was not used to generate test cases. Check if the configuration is correct.'
        )
    for unused_raw_input_file in unused_raw_input_files:
        logger.warning(
            f'"{unused_raw_input_file}" was not used as input. Check if the configuration is correct.'
        )