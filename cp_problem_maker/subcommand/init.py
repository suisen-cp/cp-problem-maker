import argparse
from pathlib import Path

from cp_problem_maker.problem import Problem


def add_parser(subparsers):
    parser_init: argparse.ArgumentParser = subparsers.add_parser(
        "init",
        description="create template"
    )
    parser_init.add_argument(
        "-p", "--path",
        type=str,
        default="."
    )

def run(path: Path):
    Problem(path).create_problem()
