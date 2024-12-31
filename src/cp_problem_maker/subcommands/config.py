import argparse
import sys
from typing import Any

import toml

from cp_problem_maker.config.tool_config import GLOBAL_CONFIG_PATH, load_global_config
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.utils import _pydantic

_COMMAND_NAME = "config"

logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME,
        help="Change the global settings",
        description="Change the global settings",
    )
    parser.add_argument(
        "key",
        help="Key of the option. Keys are specified like 'language.cpp.flags'. If set to '.', show the whole config.",  # noqa: E501
    )
    parser.add_argument(
        "value",
        help="Value of the option. If not given, get the value of the option",
        nargs="?",
        default=None,
    )

    return parser


def run(args: argparse.Namespace) -> None:
    logger.debug("Passed key: %s", args.key)
    logger.debug("Passed value: %s", args.value)
    keys = args.key.split(".") if args.key != "." else []
    val = args.value
    if val is not None:
        logger.info("Setting %s to %s", args.key, val)
    else:
        logger.info("Getting %s", args.key)

    user_config = load_global_config()
    update_dict: dict[str, Any] = dict()

    if val is not None:
        sub_config_dict = update_dict
        for key in keys[:-1]:
            sub_config_dict = sub_config_dict.setdefault(key, {})
        sub_config_dict[keys[-1]] = val

    _pydantic.update_model(user_config, update_dict)

    if val is None:
        attr = _pydantic.ModelAttributeAccessor.get_attr(user_config, keys)
        if _pydantic.ModelAttributeAccessor._is_branch(attr):
            toml.dump(attr.model_dump(mode="json"), sys.stdout)
        else:
            print(repr(attr))
    else:
        logger.info("Writing the new config to %s", GLOBAL_CONFIG_PATH)
        with GLOBAL_CONFIG_PATH.open(mode="w") as f:
            toml.dump(user_config.model_dump(mode="json", exclude_defaults=True), f)
