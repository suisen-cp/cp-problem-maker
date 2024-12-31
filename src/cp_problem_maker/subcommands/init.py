import argparse
from pathlib import Path

from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.project.problem import ProblemWithConfig

_COMMAND_NAME = "init"

logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME,
        help="Initialize a new project",
        description="Initialize a new project",
    )
    parser.add_argument("-p", "--path", help="Path to the project")
    parser.add_argument(
        "--search-root", action="store_true", help="Search for the root of the project"
    )
    return parser


def run(args: argparse.Namespace) -> None:
    path: Path | None = None
    if args.path is not None:
        path = Path(args.path)
    init(path, search_root=args.search_root)


def init(path: Path | None, *, search_root: bool) -> None:
    logger.debug("Passed path: %s", path)
    logger.info("Initializing a new problem")
    problem_with_config = ProblemWithConfig(path, search_root=search_root)
    problem_with_config.problem.init_problem()
