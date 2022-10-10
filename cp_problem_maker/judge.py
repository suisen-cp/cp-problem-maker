from asyncio.subprocess import DEVNULL
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired, check_call
from time import perf_counter_ns
from typing import List, Optional

from cp_problem_maker.config import Config, SolutionConfig
from cp_problem_maker.util import pathlib_util

logger: logging.Logger = logging.getLogger(__name__)


class UnexpectedRuntimeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnexpectedTimeLimitExceeded(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnexpectedWrongAnswer(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class JudgeStatus(Enum):
    AC = 0
    WA = 1
    TLE = 2
    RE = 3

    def __str__(self) -> str:
        return self.name


@dataclass
class JudgeResult:
    status: JudgeStatus
    elapsed_ms: int


def _exec_solution_cmd(solution_file: Path) -> List[str]:
    return [
        f'{solution_file.with_suffix("")}'
    ]


def _check_cmd(*, checker_file: Path, input_file: Path, output_file_expected: Path, output_file_actual: Path) -> List[str]:
    checker_exe_file = checker_file.with_suffix('')
    return [
        f'{checker_exe_file}',
        f'{input_file}',
        f'{output_file_expected}',
        f'{output_file_actual}',
    ]


def judge(
    *,
    input_file: Path,
    output_file: Path,
    solution_file: Path,
    checker_file: Optional[Path] = None,
    output_file_expected: Optional[Path] = None,
    config: Config,
    parents=False,
    exist_ok=False,
) -> JudgeResult:
    assert not ((checker_file is None) ^ (output_file_expected is None))

    pathlib_util.ensure_file(input_file)
    if not parents:
        pathlib_util.ensure_dir(output_file.parent)
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
    if not exist_ok:
        pathlib_util.ensure_not_exists(output_file)

    if solution_file.name not in config.solution_config:
        raise ValueError(
            f'Configuration About the Solution "{solution_file.name}" Not Found.')

    solution_config = config.solution_config[solution_file.name]
    logger.info(f"  solution: {solution_file.name}")
    logger.info(f"  config  : {solution_config}")
    logger.info(f"  input   : {input_file.name}")

    start_time = perf_counter_ns()
    try:
        check_call(
            _exec_solution_cmd(solution_file),
            stdin=open(input_file),
            stdout=open(output_file, mode='w'),
            timeout=config.timelimit
        )
        status = JudgeStatus.AC
    except CalledProcessError:
        status = JudgeStatus.RE
    except TimeoutExpired:
        status = JudgeStatus.TLE
    elapsed_ms = (perf_counter_ns() - start_time) // (10 ** 6)

    if status == JudgeStatus.AC and checker_file is not None and output_file_expected is not None:
        pathlib_util.ensure_file(checker_file)
        pathlib_util.ensure_file(output_file_expected)
        try:
            check_call(
                _check_cmd(
                    checker_file=checker_file,
                    input_file=input_file,
                    output_file_expected=output_file_expected,
                    output_file_actual=output_file
                ),
                stderr=DEVNULL
            )
        except CalledProcessError:
            status = JudgeStatus.WA

    return JudgeResult(status=status, elapsed_ms=elapsed_ms)


def assert_judge_status(status: JudgeStatus, solution_config: SolutionConfig) -> None:
    if status == JudgeStatus.TLE and not solution_config.allow_tle:
        raise UnexpectedTimeLimitExceeded()
    if status == JudgeStatus.WA and not solution_config.wrong:
        raise UnexpectedWrongAnswer()
