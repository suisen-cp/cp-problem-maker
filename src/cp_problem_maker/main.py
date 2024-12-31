import argparse

from cp_problem_maker import subcommands
from cp_problem_maker.logging.setup import get_logger

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tools for creating competitive programming problems"
    )
    subparsers = parser.add_subparsers(required=True, dest=subcommands.SUBCOMMAND_DEST)
    subcommands.add_parsers(subparsers)
    args = parser.parse_args()
    try:
        subcommands.run(args)
    except Exception as e:
        logger.exception(e)
        raise e
