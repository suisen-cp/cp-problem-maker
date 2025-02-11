import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from cp_problem_maker.buildrun.languages import (
    ILanguage,
    LanguageRegistry,
    TextCat,
)
from cp_problem_maker.buildrun.languages.cpp import Cpp, SolverCpp
from cp_problem_maker.buildrun.runners.generator import (
    GeneratorParams,
    ITestcaseGenerator,
    RawTestcaseGenerator,
    SourceTestcaseGenerator,
)
from cp_problem_maker.buildrun.runners.runner import RunnerParams
from cp_problem_maker.buildrun.runners.solver import SourceTestcaseSolver
from cp_problem_maker.buildrun.runners.verifier import SourceTestcaseVerifier
from cp_problem_maker.config import problem_config
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.project.problem import Problem, ProblemWithConfig
from cp_problem_maker.subcommands import check, gen_params

_COMMAND_NAME = "gen-cases"

logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME, help="Generate test cases", description="Generate test cases"
    )
    parser.add_argument("-p", "--path", help="Path to the project")
    parser.add_argument(
        "--error-on-unused", action="store_true", help="Error on unused generators"
    )
    parser.add_argument(
        "--no-update-params", action="store_true", help="Do not update the parameters"
    )
    parser.add_argument(
        "--no-check", action="store_true", help="Do not check the answers"
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Generate test cases for the interactive problem",
    )
    parser.add_argument("-s", "--solver", help="Path to the answer generator.")
    return parser


def run(args: argparse.Namespace) -> None:
    path: Path | None = None
    if args.path is not None:
        path = Path(args.path)
    if not args.no_update_params:
        gen_params.gen_params(path)
    gen_cases(
        path,
        solver=Path(args.solver) if args.solver is not None else None,
        error_on_unused=args.error_on_unused,
        interactive=args.interactive,
        no_check=args.no_check,
    )


@dataclass
class _GeneratorParams:
    generator_type: type[ITestcaseGenerator]
    cmd: list[str]
    test_name: str
    test_id: int
    inputs_dir: Path


@dataclass
class _VerifierParams:
    file: Path


@dataclass
class _SolutionParams:
    file: Path | None
    answers_dir: Path
    timeout: float
    memory_limit: int | None


def _generator_type(lang_type: type[ILanguage]) -> type[ITestcaseGenerator]:
    if lang_type == TextCat:
        return RawTestcaseGenerator
    return SourceTestcaseGenerator


def _generate_input(*, params: _GeneratorParams) -> Path:
    dest_file = Problem.input_file(params.inputs_dir, params.test_name, params.test_id)
    logger.info("Generating input file '%s'", dest_file.name)
    with dest_file.open("w") as f:
        params.generator_type.generate_testcase(
            params.cmd,
            generator_params=GeneratorParams(
                case_group=params.test_name, case_id=params.test_id
            ),
            runner_params=RunnerParams(stdout=f, check_returncode=True),
        )
    return dest_file


def _verify_testcase(testcase_file: Path, *, params: _VerifierParams) -> None:
    logger.info(
        "Verifying testcase %s by the verifier %s", testcase_file.name, params.file.name
    )
    lang = LanguageRegistry.get_languege(params.file)
    exec_cmd = lang.compile(params.file).exec_cmd
    with testcase_file.open() as f:
        SourceTestcaseVerifier.verify_testcase(
            exec_cmd, runner_params=RunnerParams(stdin=f, check_returncode=True)
        )


def _generate_answer(testcase_file: Path, *, params: _SolutionParams) -> None:
    output_file = (params.answers_dir / testcase_file.name).with_suffix(".out")

    if params.file is None:
        logger.warning("No solver is provided. Answer file will be the same as input.")
        shutil.copy(testcase_file, output_file)
        return

    logger.info(
        "Generating answer for testcase %s by the solution %s",
        testcase_file.name,
        params.file.name,
    )
    lang = LanguageRegistry.get_languege(params.file)
    if isinstance(lang, Cpp):
        lang = LanguageRegistry.get_languege(SolverCpp)
    exec_cmd = lang.compile(params.file).exec_cmd
    with testcase_file.open(mode="r") as inf, output_file.open(mode="w") as ouf:
        SourceTestcaseSolver.solve_testcase(
            exec_cmd,
            runner_params=RunnerParams(
                stdin=inf,
                stdout=ouf,
                check_returncode=True,
                timeout=params.timeout,
                memory_limit=params.memory_limit,
            ),
        )


def _generate_testcase(
    *,
    generator_params: _GeneratorParams,
    verifier_params: _VerifierParams,
    solution_params: _SolutionParams,
) -> Path:
    testcase_file = _generate_input(params=generator_params)
    _verify_testcase(testcase_file, params=verifier_params)
    _generate_answer(testcase_file, params=solution_params)
    return testcase_file


def _generate_testcases(
    test: problem_config._Test,
    *,
    generators_dir: Path,
    inputs_dir: Path,
    verifier_params: _VerifierParams,
    solution_params: _SolutionParams,
) -> tuple[list[Path], list[str]]:
    logger.info("Generating %d test cases for the group: %s", test.number, test.name)
    generator_file = generators_dir / test.name
    generator_lang_type: type[ILanguage] = ILanguage.detect_language(generator_file)
    generator_type = _generator_type(generator_lang_type)
    generator_lang = LanguageRegistry.get_languege(generator_lang_type)
    generator_cmd = generator_lang.compile(generator_file).exec_cmd
    is_textcat = generator_lang_type == TextCat

    generator_params = _GeneratorParams(
        generator_type=generator_type,
        cmd=generator_cmd,
        test_name=test.name,
        test_id=0,
        inputs_dir=inputs_dir,
    )

    input_files: list[Path] = []
    used_generators = []
    for test_id in range(test.number):
        generator_params.test_id = test_id
        if is_textcat:
            raw_input_file = Problem.input_file(
                generators_dir, test.name, test_id
            ).with_suffix(generator_file.suffix)
            generator_params.cmd = TextCat().compile(raw_input_file).exec_cmd
        input_file = _generate_testcase(
            generator_params=generator_params,
            verifier_params=verifier_params,
            solution_params=solution_params,
        )
        input_files.append(input_file)
        if is_textcat:
            used_generators.append(input_file.name)
    if not is_textcat:
        used_generators.append(test.name)
        used_generators.append(Path(test.name).stem)

    return input_files, used_generators


def gen_cases(
    path: Path | None,
    *,
    solver: Path | None = None,
    error_on_unused: bool,
    interactive: bool,
    no_check: bool,
) -> None:
    logger.debug("Passed path: %s", path)
    logger.info("Generating test cases")

    if interactive and solver is None:
        logger.warning(
            "Solver is missing for the interactive problem. Answer files will be the same as input."  # noqa: E501
        )

    problem_with_config = ProblemWithConfig(path, search_root=True)
    problem = problem_with_config.problem
    problem_cfg = problem_with_config.problem_config
    cfg = problem_with_config.config
    LanguageRegistry.load_config(cfg.language)

    verifier_file = problem.verifier_file
    verifier_params = _VerifierParams(file=verifier_file)

    solution_file: Path | None = None
    if solver is not None:
        solution_file = solver
    elif not interactive:
        solution_file = problem.solutions_dir / problem_cfg.expected_solution.name
    solution_params = _SolutionParams(
        file=solution_file,
        answers_dir=problem.outputs_dir,
        timeout=problem_cfg.timelimit,
        memory_limit=problem_cfg.memorylimit,
    )

    unused_generators = set(
        f.name for f in problem.generators_dir.iterdir() if f.is_file()
    )

    for test in problem_cfg.tests:
        _, used_generators = _generate_testcases(
            test,
            generators_dir=problem.generators_dir,
            inputs_dir=problem.inputs_dir,
            verifier_params=verifier_params,
            solution_params=solution_params,
        )
        unused_generators -= set(used_generators)

    if unused_generators:
        if error_on_unused:
            raise ValueError(f"Unused generators: {sorted(unused_generators)}")
        logger.warning("Unused generator: %s", sorted(unused_generators))

    if not no_check:
        check.check(
            path,
            [problem_cfg.expected_solution.name],
            check_all=False,
            no_stderr=False,
            interactive=interactive,
        )
