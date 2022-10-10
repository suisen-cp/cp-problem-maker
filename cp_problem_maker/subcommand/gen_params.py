import argparse
from logging import Logger, getLogger
from pathlib import Path
from typing import Set

from cp_problem_maker.problem import Problem
from cp_problem_maker.config import Config


logger: Logger = getLogger(__name__)


def add_parser(subparsers):
    parser_gen: argparse.ArgumentParser = subparsers.add_parser(
        "gen-params", description="generate params.h"
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


def run(path: Path, *, exist_ok=False):
    problem = Problem(path)
    config = Config(problem.config_file)

    try:
        config.write_params(problem.params_file, exist_ok=exist_ok)
    except FileExistsError as e:
        logger.exception(e)
        logger.error(
            "If you want to allow file replacement, give the '--allow-replace' flag."
        )
        exit(1)
