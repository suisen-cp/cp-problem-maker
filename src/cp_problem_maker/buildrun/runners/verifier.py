import abc
from enum import IntEnum

from pydantic import BaseModel, ConfigDict

from cp_problem_maker.buildrun.runners import runner


class VerifierStatusEnum(IntEnum):
    Passed = 0
    Failed = 1


class VerifyResult(BaseModel):
    run_result: runner.RunResult
    status: VerifierStatusEnum

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ITestcaseVerifier(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def _verifier_cmd(
        cls,
        cmd: list[str],
    ) -> list[str]:
        """Generate the command to run the verifier

        Args:
            cmd (list[str]): Command to run the verifier
        Returns:
            list[str]: Command to run the verifier
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def verify_testcase(
        cls,
        cmd: list[str],
        *,
        runner_params: runner.RunnerParams,
    ) -> VerifyResult:
        """Verify the test case

        Args:
            cmd (list[str]): Command to run the verifier
            runner_params (runner.RunnerParams): Parameter set for running the verifier
        Returns:
            VerifyResult: Result of the verification
        """
        raise NotImplementedError()


class SourceTestcaseVerifier(ITestcaseVerifier):
    @classmethod
    def _verifier_cmd(
        cls,
        cmd: list[str],
    ) -> list[str]:
        return cmd

    @classmethod
    def verify_testcase(
        cls,
        cmd: list[str],
        *,
        runner_params: runner.RunnerParams,
    ) -> VerifyResult:
        run_result = runner.run(cls._verifier_cmd(cmd), runner_params=runner_params)
        if run_result.returncode == 0:
            status = VerifierStatusEnum.Passed
        else:
            status = VerifierStatusEnum.Failed
        return VerifyResult(
            run_result=run_result,
            status=status,
        )
