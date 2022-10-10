import argparse
from pathlib import Path

from cp_problem_maker.subcommand import gen_case
from cp_problem_maker.subcommand import check


def add_parser(subparsers):
    parser_test: argparse.ArgumentParser = subparsers.add_parser(
        "test", description="generates and verifies inputs, generates outputs, and checks other solutions")
    parser_test.add_argument(
        "-p", "--path",
        type=str,
        default="."
    )
    parser_test.add_argument(
        "--allow-replace",
        action="store_true"
    )

def run(path: Path, *, parents=False, exist_ok=False):
    gen_case.run(path, parents=parents, exist_ok=exist_ok)
    check.run(path, [])