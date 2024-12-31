import abc
import subprocess
from enum import Enum

from pydantic import BaseModel, ConfigDict

from cp_problem_maker.buildrun.runners import runner


class SolverStatusEnum(Enum):
    Success = "Success"
    Fail = "Fail"
    Timeout = "Timeout"


class SolveResult(BaseModel):
    run_result: runner.RunResult | None
    """Result of running the solver. None if the solver failed to run."""
    status: SolverStatusEnum

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ITestcaseSolver(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def _solver_cmd(
        cls,
        cmd: list[str],
    ) -> list[str]:
        """Generate the command to run the solver

        Args:
            cmd (list[str]): Command to run the solver
        Returns:
            list[str]: Command to run the solver
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def solve_testcase(
        cls,
        cmd: list[str],
        *,
        runner_params: runner.RunnerParams,
    ) -> SolveResult:
        """Solve the test case

        Args:
            cmd (list[str]): Command to run the solver
            runner_params (runner.RunnerParams): Parameter set for running the solver
        """
        raise NotImplementedError()


class SourceTestcaseSolver(ITestcaseSolver):
    @classmethod
    def _solver_cmd(
        cls,
        cmd: list[str],
    ) -> list[str]:
        return cmd

    @classmethod
    def solve_testcase(
        cls,
        cmd: list[str],
        *,
        runner_params: runner.RunnerParams,
    ) -> SolveResult:
        try:
            run_result = runner.run(cls._solver_cmd(cmd), runner_params=runner_params)
        except subprocess.TimeoutExpired:
            return SolveResult(run_result=None, status=SolverStatusEnum.Timeout)
        except subprocess.CalledProcessError:
            return SolveResult(run_result=None, status=SolverStatusEnum.Fail)
        if run_result.returncode != 0:
            return SolveResult(run_result=run_result, status=SolverStatusEnum.Fail)
        return SolveResult(run_result=run_result, status=SolverStatusEnum.Success)
