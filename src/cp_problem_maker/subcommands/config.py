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
        help="Scope of the option. Use 'global' for global settings, 'local' for local settings",  # noqa: E501
        choices=["global", "local"],
    )
    parser.add_argument(
        "key",
        help="The key of the option. Use dot notation like 'language.cpp.flags'. Use '.' to display the entire configuration.",  # noqa: E501
    )
    parser.add_argument(
        "value",
        help="The value of the option. If omitted, the current value will be retrieved.",  # noqa: E501
        nargs="?",
    )
    parser.add_argument(
        "--values",
        help="Specify multiple values as a space-separated list for list-type options.",
        nargs=argparse.REMAINDER,
    )
    parser.add_argument(
        "--space-separated",
        help="Get the value as a space-separated list (for list-type values).",
        action="store_true",
    )

    return parser


def run(args: argparse.Namespace) -> None:
    logger.debug("Passed scope: %s", args.scope)
    logger.debug("Passed key: %s", args.key)
    logger.debug("Passed value: %s", args.value)
    scope: Literal["global", "local"] = args.scope
    key: list[str] = args.key.split(".") if args.key != "." else []
    val = args.value
    vals = args.values
    space_separated = args.space_separated

    if vals is not None and val is not None:
        logger.error("Cannot specify both value and --values")
        return
    if vals is not None:
        val = vals
    if val is not None:
        logger.info("Setting %s to %s", args.key, val)
    else:
        logger.info("Getting %s", args.key)

    if val is not None and space_separated:
        logger.error("--space-separated option is only available for getting values.")
        return

    config(scope, key, val, space_separated=space_separated)


def config(
    scope: Literal["global", "local"],
    key: list[str],
    value: Any | None,
    *,
    space_separated: bool = False,
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
            if isinstance(attr, list) and space_separated:
                print(" ".join(attr))
            else:
                if space_separated:
                    logger.warning("The value is not a list-type value.")
                print(repr(attr))
    else:
        logger.info("Writing the new config to %s", config_path)
        with config_path.open(mode="w") as f:
            toml.dump(dump_values, f)
