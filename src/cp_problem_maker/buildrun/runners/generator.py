import abc
import hashlib

from pydantic import BaseModel, ConfigDict, Field

from cp_problem_maker.buildrun.runners import runner


class GeneratorParams(BaseModel):
    """Parameters for generating test cases"""

    case_group: str = Field(..., description="Group of the test case")
    case_id: int = Field(..., description="ID of the test case in the group")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ITestcaseGenerator(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def _random_seed(cls, *, generator_params: GeneratorParams) -> int:
        """Generate the 31bit seed for the test case

        Args:
            generator_params (GeneratorParams): Parameters for generating test cases
        Returns:
            int: 31bit seed for the test case
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def _generator_cmd(
        cls,
        cmd: list[str],
        *,
        generator_params: GeneratorParams,
    ) -> list[str]:
        """Generate the command to run the generator

        Args:
            cmd (list[str]): Command to run the generator
            generator_params (GeneratorParams): Parameters for generating test cases
        Returns:
            list[str]: Command to run the generator
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def generate_testcase(
        cls,
        cmd: list[str],
        *,
        generator_params: GeneratorParams,
        runner_params: runner.RunnerParams,
    ) -> runner.RunResult:
        """Generate the test case

        Args:
            cmd (list[str]): Command to run the generator
            generator_params (GeneratorParams): Parameters for generating test cases
            runner_params (runner.RunnerParams): Parameter set for running the generator
        Returns:
            runner.RunResult: Result of the generation
        """
        raise NotImplementedError()


class SourceTestcaseGenerator(ITestcaseGenerator):
    @classmethod
    def _random_seed(cls, *, generator_params: GeneratorParams) -> int:
        seed_str = f"{generator_params.case_group}{generator_params.case_id}"
        hex_str = hashlib.sha256(seed_str.encode()).hexdigest()
        seed = 0
        for i in range(0, len(hex_str), 8):
            seed ^= int(hex_str[i: i + 8], 16)
        seed &= 0x7fff_ffff  # 31bit
        return seed

    @classmethod
    def _generator_cmd(
        cls,
        cmd: list[str],
        *,
        generator_params: GeneratorParams,
    ) -> list[str]:
        return cmd + [
            str(generator_params.case_id),
            str(cls._random_seed(generator_params=generator_params)),
        ]

    @classmethod
    def generate_testcase(
        cls,
        cmd: list[str],
        *,
        generator_params: GeneratorParams,
        runner_params: runner.RunnerParams,
    ) -> runner.RunResult:
        return runner.run(
            cls._generator_cmd(cmd, generator_params=generator_params),
            runner_params=runner_params,
        )


class RawTestcaseGenerator(ITestcaseGenerator):
    @classmethod
    def _generator_cmd(
        cls, cmd: list[str], *, generator_params: GeneratorParams
    ) -> list[str]:
        return cmd

    @classmethod
    def _random_seed(cls, *, generator_params: GeneratorParams) -> int:
        return 0

    @classmethod
    def generate_testcase(
        cls,
        cmd: list[str],
        *,
        generator_params: GeneratorParams,
        runner_params: runner.RunnerParams,
    ) -> runner.RunResult:
        return runner.run(
            cls._generator_cmd(cmd, generator_params=generator_params),
            runner_params=runner_params,
        )
