import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping, Optional

from pydantic import BaseModel, ConfigDict

from cp_problem_maker.buildrun.languages.cpp import Cpp, SolverCpp
from cp_problem_maker.buildrun.languages.registry import LanguageRegistry
from cp_problem_maker.buildrun.runners.checker import (
    CheckerParams,
    CheckerStatusEnum,
    CheckResult,
    ITestcaseChecker,
    get_checker_type,
)
from cp_problem_maker.buildrun.runners.runner import RunnerParams, RunResult
from cp_problem_maker.buildrun.runners.solver import (
    SolveResult,
    SolverStatusEnum,
    SourceTestcaseSolver,
)
from cp_problem_maker.config import problem_config
from cp_problem_maker.logging.setup import get_logger
from cp_problem_maker.project.problem import Problem, ProblemWithConfig

_COMMAND_NAME = "check"

logger = get_logger(__name__)


def add_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        _COMMAND_NAME, help="Check the solutions", description="Check the solutions"
    )
    parser.add_argument("targets", nargs="*", help="Targets to check")
    parser.add_argument("--all", action="store_true", help="Check all the solutions")
    parser.add_argument("-p", "--path", help="Path to the project")
    parser.add_argument(
        "--no-stderr",
        action="store_true",
        help="Suppress stderr of the solver and the checker",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    path: Path | None = None
    if args.path is not None:
        path = Path(args.path)
    check(path, args.targets, check_all=args.all, no_stderr=args.no_stderr)


class CheckError(Exception):
    pass


def _get_target_solutions(
    targets: list[str],
    *,
    all_solutions: bool,
    solutions_config: list[problem_config._Solution],
) -> list[problem_config._Solution]:
    target_solutions: list[problem_config._Solution] = []
    if all_solutions:
        target_solutions = solutions_config
    else:
        for target in targets:
            for solution in solutions_config:
                if solution.name == target:
                    target_solutions.append(solution)
                    break
            else:
                raise ValueError(f"Solution '{target}' has no configuration.")
        if not target_solutions:
            target_solutions = solutions_config

    return target_solutions


def _check_solutions_existence(
    target_solutions: list[problem_config._Solution], *, solutions_dir: Path
) -> None:
    for solution in target_solutions:
        solution_file = solutions_dir / solution.name
        if not solution_file.exists():
            raise ValueError(f"Solution '{solution_file}' not found.")


class JudgeStatusEnum(Enum):
    Accepted = "AC"
    WrongAnswer = "WA"
    RuntimeError = "RE"
    TimeLimitExceeded = "TLE"
    PresentationError = "PE"
    Fail = "FAIL"


class JudgeResult(BaseModel):
    run_result: Optional[RunResult]
    status: JudgeStatusEnum

    model_config = ConfigDict(frozen=True, extra="forbid")

    def pretty_print_str(self) -> str:
        lines: list[str] = []
        lines.append(f"Status = {self.status.value}")
        if self.run_result is not None:
            lines.append(f"Time = {self.run_result.elapsed_time * 1000:.0f} ms")
            lines.append(f"Memory = {self.run_result.used_memory_mb:.0f} MiB")
        else:
            lines.append("Time = N/A ms")
            lines.append("Memory = N/A MiB")
        return ", ".join(lines)


class JudgeSummary(BaseModel):
    status_count: Mapping[JudgeStatusEnum, int]
    max_time: float
    max_memory: float


@dataclass
class _SolutionParams:
    file: Path
    timeout: float
    memory_limit: int | None
    no_stderr: bool


@dataclass
class _CheckerParams:
    checker: ITestcaseChecker
    checker_file: Path
    input_file: Path
    output_file: Path
    answer_file: Path
    no_stderr: bool


def _solve(
    input_file: Path, output_file: Path, *, params: _SolutionParams
) -> SolveResult:
    logger.info(
        "Solving the testcase %s by the solution %s", input_file.name, params.file.name
    )
    lang = LanguageRegistry.get_languege(params.file)
    if isinstance(lang, Cpp):
        lang = LanguageRegistry.get_languege(SolverCpp)
    exec_cmd = lang.compile(params.file).exec_cmd
    with input_file.open("r") as inf, output_file.open("w") as ouf:
        solve_result = SourceTestcaseSolver.solve_testcase(
            cmd=exec_cmd,
            runner_params=RunnerParams(
                stdin=inf,
                stdout=ouf,
                stderr=Path(os.devnull).open("w") if params.no_stderr else sys.stderr,
                check_returncode=False,
                timeout=params.timeout,
                memory_limit=params.memory_limit,
            ),
        )
    return solve_result


def _check(checker: ITestcaseChecker, *, params: _CheckerParams) -> CheckResult:
    logger.info(
        "Checking the testcase %s by the checker %s",
        params.input_file.name,
        params.checker_file.name,
    )
    checker_lang = LanguageRegistry.get_languege(params.checker_file)
    checker_cmd = checker_lang.compile(params.checker_file).exec_cmd
    with params.output_file.open("r") as ouf:
        check_result = checker.check_testcase(
            cmd=checker_cmd,
            checker_params=CheckerParams(
                input_file=params.input_file,
                output_file=params.output_file,
                answer_file=params.answer_file,
            ),
            runner_params=RunnerParams(
                stdin=ouf,
                stderr=Path(os.devnull).open("w") if params.no_stderr else sys.stderr,
                check_returncode=False,
            ),
        )
    return check_result


def _judge(
    *,
    checker_params: _CheckerParams,
    solution_params: _SolutionParams,
) -> JudgeResult:
    solve_result = _solve(
        checker_params.input_file,
        checker_params.output_file,
        params=solution_params,
    )
    match solve_result.status:
        case SolverStatusEnum.Success:
            pass
        case SolverStatusEnum.Fail:
            return JudgeResult(
                run_result=solve_result.run_result,
                status=JudgeStatusEnum.RuntimeError,
            )
        case SolverStatusEnum.Timeout:
            return JudgeResult(
                run_result=solve_result.run_result,
                status=JudgeStatusEnum.TimeLimitExceeded,
            )
        case _:
            raise ValueError(f"Unsupported status {solve_result.status}")

    check_status = _check(checker=checker_params.checker, params=checker_params).status
    match check_status:
        case CheckerStatusEnum.Accepted:
            status = JudgeStatusEnum.Accepted
        case CheckerStatusEnum.WrongAnswer:
            status = JudgeStatusEnum.WrongAnswer
        case CheckerStatusEnum.PresentationError:
            status = JudgeStatusEnum.PresentationError
        case CheckerStatusEnum.Fail:
            status = JudgeStatusEnum.Fail
        case _:
            raise ValueError(f"Unsupported status {check_status}")
    return JudgeResult(run_result=solve_result.run_result, status=status)


def _judge_all_tests(
    tests: list[problem_config._Test],
    *,
    inputs_dir: Path,
    outputs_dir: Path,
    solution_params: _SolutionParams,
    checker: ITestcaseChecker,
    checker_file: Path,
    no_stderr: bool,
) -> JudgeSummary:
    max_time = 0.0
    max_memory = 0.0
    status_count: defaultdict[JudgeStatusEnum, int] = defaultdict(int)
    for test in tests:
        for test_id in range(test.number):
            input_file = Problem.input_file(inputs_dir, test.name, test_id)
            answer_file = Problem.output_file(outputs_dir, test.name, test_id)
            with NamedTemporaryFile() as tmpfile:
                output_file = Path(tmpfile.name)
                judge_result = _judge(
                    checker_params=_CheckerParams(
                        checker=checker,
                        checker_file=checker_file,
                        input_file=input_file,
                        output_file=output_file,
                        answer_file=answer_file,
                        no_stderr=no_stderr,
                    ),
                    solution_params=solution_params,
                )
            logger.info(judge_result.pretty_print_str())
            status_count[judge_result.status] += 1
            if judge_result.run_result is not None:
                max_time = max(max_time, judge_result.run_result.elapsed_time)
                max_memory = max(max_memory, judge_result.run_result.used_memory_mb)
    return JudgeSummary(
        status_count=status_count, max_time=max_time, max_memory=max_memory
    )


def _collect_error_messages(
    solution: problem_config._Solution, status_count: Mapping[JudgeStatusEnum, int]
) -> list[str]:
    msg_lines: list[str] = []

    wa_count = status_count.get(JudgeStatusEnum.WrongAnswer, 0)
    tle_count = status_count.get(JudgeStatusEnum.TimeLimitExceeded, 0)
    re_count = status_count.get(JudgeStatusEnum.RuntimeError, 0)
    match solution.wa:
        case "never":
            if wa_count:
                msg_lines.append("'wa' is set to 'never', but there is WA")
        case "expected":
            if not wa_count:
                msg_lines.append("'wa' is set to 'expected', but there is no WA")
    match solution.tle:
        case "never":
            if tle_count:
                msg_lines.append("'tle' is set to 'never', but there is TLE")
        case "expected":
            if not tle_count:
                msg_lines.append("'tle' is set to 'expected', but there is no TLE")
    match solution.re:
        case "never":
            if re_count:
                msg_lines.append("'re' is set to 'never', but there is RE")
        case "expected":
            if not re_count:
                msg_lines.append("'re' is set to 'expected', but there is no RE")
    return msg_lines


def _summary_message(judge_summary: JudgeSummary) -> str:
    status_count = judge_summary.status_count
    counts_joined = ", ".join(
        f"{status.value}:{count}" for status, count in status_count.items()
    )
    status_summary = "{" + counts_joined + "}"
    is_tle = status_count.get(JudgeStatusEnum.TimeLimitExceeded, 0) > 0
    time_summary = "N/A ms" if is_tle else f"{judge_summary.max_time * 1000:.0f} ms"
    memory_summary = f"{judge_summary.max_memory:.0f} MiB"
    return f"Status={status_summary}, Time={time_summary}, Memory={memory_summary}"


def check(
    path: Path | None, targets: list[str], *, check_all: bool, no_stderr: bool
) -> None:
    logger.debug("Passed path: %s", path)
    logger.debug("Passed targets: %s", targets)
    logger.debug("Check all: %s", check_all)
    logger.info("Checking the solutions")

    problem_with_config = ProblemWithConfig(path, search_root=True)
    problem = problem_with_config.problem
    problem_cfg = problem_with_config.problem_config
    cfg = problem_with_config.config
    LanguageRegistry.load_config(cfg.language)

    target_solutions: list[problem_config._Solution] = _get_target_solutions(
        targets, all_solutions=check_all, solutions_config=problem_cfg.solutions
    )
    if not target_solutions:
        raise ValueError("No solution to check")
    _check_solutions_existence(target_solutions, solutions_dir=problem.solutions_dir)

    checker_type: type[ITestcaseChecker] = get_checker_type(cfg.checker.style)
    checker = checker_type(cfg.checker)

    error_messages: dict[str, list[str]] = {}
    summary_messages: dict[str, str] = {}
    for solution in target_solutions:
        solution_params = _SolutionParams(
            file=problem.solutions_dir / solution.name,
            timeout=problem_cfg.timelimit,
            memory_limit=problem_cfg.memorylimit,
            no_stderr=no_stderr,
        )
        judge_summary = _judge_all_tests(
            problem_cfg.tests,
            inputs_dir=problem.inputs_dir,
            outputs_dir=problem.outputs_dir,
            solution_params=solution_params,
            checker=checker,
            checker_file=problem.checker_file,
            no_stderr=no_stderr,
        )
        error_messages[solution.name] = _collect_error_messages(
            solution, judge_summary.status_count
        )
        summary_msg = _summary_message(judge_summary)
        summary_messages[solution.name] = summary_msg
        logger.info("Summary of the solution: %s", summary_msg)

    has_error = False
    for name, error_msgs in error_messages.items():
        summary_msg = summary_messages[name]
        logger.info("Summary of the solution '%s': %s", name, summary_msg)
        if not error_msgs:
            logger.info("Solution '%s' has worked expectedly", name)
            continue
        has_error = True
        for msg in error_msgs:
            logger.error("Solution '%s' has the following error: %s", name, msg)
    if has_error:
        raise CheckError("Some solutions have errors")
