import argparse

from . import check as CheckCommand
from . import config as ConfigCommand
from . import gen_cases as GenCasesCommand
from . import gen_params as GenParamsCommand
from . import init as InitCommand
from . import test as TestCommand

SUBCOMMAND_DEST = "subcommand"


def add_parsers(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    CheckCommand.add_parser(subparsers)
    ConfigCommand.add_parser(subparsers)
    GenCasesCommand.add_parser(subparsers)
    GenParamsCommand.add_parser(subparsers)
    InitCommand.add_parser(subparsers)
    TestCommand.add_parser(subparsers)


def run(args: argparse.Namespace) -> None:
    subcommand: str = getattr(args, SUBCOMMAND_DEST)
    match subcommand:
        case CheckCommand._COMMAND_NAME:
            CheckCommand.run(args)
        case ConfigCommand._COMMAND_NAME:
            ConfigCommand.run(args)
        case GenCasesCommand._COMMAND_NAME:
            GenCasesCommand.run(args)
        case GenParamsCommand._COMMAND_NAME:
            GenParamsCommand.run(args)
        case InitCommand._COMMAND_NAME:
            InitCommand.run(args)
        case TestCommand._COMMAND_NAME:
            TestCommand.run(args)
        case _:
            raise ValueError(f"Unknown subcommand: {subcommand}")
