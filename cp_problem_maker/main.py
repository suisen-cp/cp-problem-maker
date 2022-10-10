import argparse
from logging import DEBUG, basicConfig
from pathlib import Path

import colorlog

from cp_problem_maker.subcommand import init, gen_case, check, test


def main():
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'white',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler.setFormatter(formatter)
    basicConfig(
        level=DEBUG,
        handlers=[handler]
    )

    parser = argparse.ArgumentParser(
        description="tool for competitive programming problem maker"
    )
    subparsers = parser.add_subparsers(dest='subcommand')

    init.add_parser(subparsers)
    gen_case.add_parser(subparsers)
    check.add_parser(subparsers)
    test.add_parser(subparsers)

    args = parser.parse_args()

    subcommand: str = args.subcommand
    path = Path(args.path)

    if subcommand == 'init':
        init.run(path)
    elif subcommand == 'gen-case':
        gen_case.run(path, exist_ok=args.allow_replace)
    elif subcommand == 'check':
        check.run(path, args.solutions)
    elif subcommand == 'test':
        test.run(path, exist_ok=args.allow_replace)
