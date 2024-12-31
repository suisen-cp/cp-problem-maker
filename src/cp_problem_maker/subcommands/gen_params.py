import argparse
from pathlib import Path

from cp_problem_maker.config import problem_config, tool_config
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.project.problem import ProblemWithConfig

_COMMAND_NAME = "gen-params"


logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME,
        help="Generate problem parameters",
        description="Generate problem parameters",
    )
    parser.add_argument("-p", "--path", help="Path to the project")
    return parser


def run(args: argparse.Namespace) -> None:
    path: Path | None = None
    if args.path is not None:
        path = Path(args.path)
    gen_params(path)


def _declare_param(
    name: str, value: problem_config._ParameterValue, lang: tool_config._DefaultLanguage
) -> str:
    if isinstance(value, str):
        value = f'"{value}"'
    match lang:
        case "C++":
            return f"#define {name} {value}"
        case "Python":
            return f"{name} = {value}"
        case _:
            raise ValueError(f"Unknown language: {lang}")


def _declare_params(
    params: dict[str, problem_config._ParameterValue],
    lang: tool_config._DefaultLanguage,
) -> str:
    prefix_lines: list[str] = []
    suffix_lines: list[str] = []
    match lang:
        case "C++":
            prefix_lines = [
                "#ifndef CP_PROBLEM_MAKER_PARAMS_H",
                "#define CP_PROBLEM_MAKER_PARAMS_H",
            ]
            suffix_lines = ["#endif"]
        case "Python":
            pass
        case _:
            raise ValueError(f"Unknown language: {lang}")
    lines = (
        prefix_lines
        + [_declare_param(name, value, lang) for name, value in params.items()]
        + suffix_lines
        + [""]  # Add a newline at the end of the file
    )
    return "\n".join(lines)


def gen_params(path: Path | None) -> None:
    logger.debug("Passed path: %s", path)
    logger.info("Generating problem parameters")
    problem_with_config = ProblemWithConfig(path, search_root=True)
    params_file = problem_with_config.problem.params_file
    params = problem_with_config.problem_config.params
    with params_file.open(mode="w") as f:
        f.write(_declare_params(params, problem_with_config.config.language.default))
