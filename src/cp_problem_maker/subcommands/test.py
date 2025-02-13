import argparse
from pathlib import Path

from cp_problem_maker.subcommands import check, gen_cases, gen_params, init

_COMMAND_NAME = "test"


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME,
        help="Test the problems; generating testcases and checking all the solutions",
        description="Test the problems; generating testcases and checking all the solutions",  # noqa: E501
    )
    parser.add_argument("-p", "--path", help="Path to the project")
    parser.add_argument(
        "--no-stderr",
        action="store_true",
        help="Suppress stderr of the solver and the checker",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Use interactive judge",
    )
    parser.add_argument("-s", "--solver", help="Path to the answer generator.")
    return parser


def run(args: argparse.Namespace) -> None:
    path: Path | None = None
    if args.path is not None:
        path = Path(args.path)
    init.init(path, search_root=True)
    gen_params.gen_params(path)
    gen_cases.gen_cases(
        path,
        solver=Path(args.solver) if args.solver is not None else None,
        error_on_unused=True,
        interactive=args.interactive,
        no_check=False,
    )
    check.check(
        path, [], check_all=True, no_stderr=args.no_stderr, interactive=args.interactive
    )
