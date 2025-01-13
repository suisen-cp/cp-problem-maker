import argparse
import sys
from typing import Any, Literal

import toml

from cp_problem_maker.config.tool_config import GLOBAL_CONFIG_PATH, load_global_config
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.project.problem import ProblemWithConfig
from cp_problem_maker.utils import _pydantic

_COMMAND_NAME = "config"

logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME,
        help="Change the settings",
        description="Change the settings",
    )
    parser.add_argument(
        "scope",
        help="Scope of the option. 'global' for global settings, 'local' for local settings",  # noqa: E501
        choices=["global", "local"],
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
    logger.debug("Passed scope: %s", args.scope)
    logger.debug("Passed key: %s", args.key)
    logger.debug("Passed value: %s", args.value)
    scope: Literal["global", "local"] = args.scope
    key = args.key.split(".") if args.key != "." else []
    val = args.value
    if val is not None:
        logger.info("Setting %s to %s", args.key, val)
    else:
        logger.info("Getting %s", args.key)

    config(scope, key, val)


def config(
    scope: Literal["global", "local"], key: list[str], value: Any | None
) -> None:
    if scope == "global":
        user_config = load_global_config()
        config_path = GLOBAL_CONFIG_PATH
    else:
        try:
            problem_with_config = ProblemWithConfig(root=None, search_root=True)
        except FileNotFoundError:
            logger.error(
                "Could not find the root of the project. You are not in a problem directory."  # noqa: E501
            )
            return
        user_config = problem_with_config.config
        config_path = problem_with_config.problem.local_config_file
    update_dict: dict[str, Any] = dict()

    if value is not None:
        dump_values = toml.load(config_path)
        sub_dump_values = dump_values
        sub_config_dict = update_dict
        for k in key[:-1]:
            sub_dump_values = sub_dump_values.setdefault(k, {})
            sub_config_dict = sub_config_dict.setdefault(k, {})
        sub_dump_values[key[-1]] = value
        sub_config_dict[key[-1]] = value

    _pydantic.update_model(user_config, update_dict)

    if value is None:
        attr = _pydantic.ModelAttributeAccessor.get_attr(user_config, key)
        if _pydantic.ModelAttributeAccessor._is_branch(attr):
            toml.dump(attr.model_dump(mode="json"), sys.stdout)
        else:
            print(repr(attr))
    else:
        logger.info("Writing the new config to %s", config_path)
        with config_path.open(mode="w") as f:
            toml.dump(user_config.model_dump(mode="json", include=dump_values), f)
