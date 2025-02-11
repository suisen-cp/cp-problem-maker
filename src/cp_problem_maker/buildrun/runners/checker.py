import abc
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from cp_problem_maker.buildrun.runners import runner
from cp_problem_maker.config import tool_config


class CheckerStatusEnum(Enum):
    Accepted = "AC"
    WrongAnswer = "WA"
    PresentationError = "PE"
    Fail = "FAIL"


class CheckResult(BaseModel):
    run_result: runner.RunResult
    status: CheckerStatusEnum

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class CheckerParams(BaseModel):
    """Parameters for checking test cases"""

    input_file: Path
    """Input file path"""
    output_file: Path
    """Output file path (actual output)"""
    answer_file: Path
    """Answer file path (expected output)"""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ITestcaseChecker(metaclass=abc.ABCMeta):
    def __init__(self, checker_config: tool_config._Checker) -> None:
        """Initialize the checker

        Args:
            checker_config (config._Checker): Configuration for the checker
        """
        self.checker_config = checker_config

    def get_status_from_exit_code(self, exit_code: int) -> CheckerStatusEnum:
        match exit_code:
            case self.checker_config.exit_code.AC:
                return CheckerStatusEnum.Accepted
            case self.checker_config.exit_code.WA:
                return CheckerStatusEnum.WrongAnswer
            case self.checker_config.exit_code.PE:
                return CheckerStatusEnum.PresentationError
            case self.checker_config.exit_code.FAIL:
                return CheckerStatusEnum.Fail
            case _:
                raise ValueError(f"Invalid exit code: {exit_code}")

    @classmethod
    @abc.abstractmethod
    def checker_cmd(cls, cmd: list[str], *, checker_params: CheckerParams) -> list[str]:
        """Generate the command to run the checker

        Args:
            cmd (list[str]): Command to run the checker
            checker_params (CheckerParams): Parameters for checking test cases
        Returns:
            list[str]: Command to run the checker
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def check_testcase(
        self,
        cmd: list[str],
        *,
        checker_params: CheckerParams,
        runner_params: runner.RunnerParams,
    ) -> CheckResult:
        """Check the test case

        Args:
            cmd (list[str]): Command to run the checker
            checker_params (CheckerParams): Parameters for checking test cases
            runner_params (runner.RunnerParams): Parameter set for running the checker
        Returns:
            CheckResult: Result of the checking
        """
        raise NotImplementedError()


class TestlibStyleChecker(ITestcaseChecker):
    @classmethod
    def checker_cmd(cls, cmd: list[str], *, checker_params: CheckerParams) -> list[str]:
        return cmd + [
            str(checker_params.input_file),
            str(checker_params.output_file),
            str(checker_params.answer_file),
        ]

    def check_testcase(
        self,
        cmd: list[str],
        *,
        checker_params: CheckerParams,
        runner_params: runner.RunnerParams,
    ) -> CheckResult:
        run_result = runner.run(
            self.checker_cmd(cmd, checker_params=checker_params),
            runner_params=runner_params,
        )
        status = self.get_status_from_exit_code(run_result.returncode)
        return CheckResult(run_result=run_result, status=status)


class YukicoderStyleChecker(ITestcaseChecker):
    @classmethod
    def checker_cmd(cls, cmd: list[str], *, checker_params: CheckerParams) -> list[str]:
        return cmd + [
            str(checker_params.input_file),
            str(checker_params.answer_file),
        ]

    def check_testcase(
        self,
        cmd: list[str],
        *,
        checker_params: CheckerParams,
        runner_params: runner.RunnerParams,
    ) -> CheckResult:
        run_result = runner.run(
            self.checker_cmd(cmd, checker_params=checker_params),
            runner_params=runner_params,
        )
        status = self.get_status_from_exit_code(run_result.returncode)
        return CheckResult(run_result=run_result, status=status)


def get_checker_type(
    checker_style: tool_config._CheckerStyle,
) -> type[ITestcaseChecker]:
    """Get the checker type based on the style

    Args:
        checker_style (tool_config._CheckerStyle): Style of the checker
    Returns:
        type[ITestcaseChecker]: Checker type
    """
    match checker_style:
        case "testlib":
            return TestlibStyleChecker
        case "yukicoder":
            return YukicoderStyleChecker
        case _:
            raise ValueError(f"Invalid checker style: {checker_style}")
