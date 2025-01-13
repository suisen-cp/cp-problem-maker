from pathlib import Path
from typing import Literal, Optional

import pydantic
from pydantic import BaseModel, ConfigDict, Field

from cp_problem_maker import anchor
from cp_problem_maker.utils import _pydantic


class _Test(BaseModel):
    name: str = Field(..., description="Name of the test case")
    number: int = Field(..., ge=1, description="Number of the test case")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )


_JudgePolicy = Literal["expected", "allow", "never"]


class _Solution(BaseModel):
    name: str = Field(..., description="Name of the solution")
    expected: bool = Field(
        False,
        description="Whether the solution is expected. There must be exactly one expected solution.",  # noqa: E501
    )
    tle: _JudgePolicy = Field("never", description="Policy for TLE")
    wa: _JudgePolicy = Field("never", description="Policy for WA")
    re: _JudgePolicy = Field("never", description="Policy for RE")


_ParameterValue = int | float | str


class _ProblemConfig(BaseModel):
    title: str = Field(..., description="Title of the problem")

    timelimit: float = Field(2.0, gt=0, description="Time limit in seconds")
    memorylimit: Optional[int] = Field(None, gt=0, description="Memory limit in MiB")

    tests: list[_Test] = Field(..., description="List of test cases")
    solutions: list[_Solution] = Field(..., description="List of solutions")

    params: dict[str, _ParameterValue] = Field({}, description="Constant parameters")

    model_config = ConfigDict(
        revalidate_instances="always", extra="forbid", use_enum_values=True
    )

    @pydantic.field_validator("solutions")
    def _validate_expected_solution(cls, solutions: list[_Solution]) -> list[_Solution]:
        expected_solutions = [solution for solution in solutions if solution.expected]
        if len(expected_solutions) != 1:
            raise ValueError("There must be exactly one expected solution.")
        expected_solution = expected_solutions[0]
        if expected_solution.tle != "never":
            raise ValueError(
                "Policy for TLE must be 'never' for the expected solution."
            )
        if expected_solution.wa != "never":
            raise ValueError("Policy for WA must be 'never' for the expected solution.")
        if expected_solution.re != "never":
            raise ValueError("Policy for RE must be 'never' for the expected solution.")
        return solutions

    @property
    def expected_solution(self) -> _Solution:
        expected_solutions = list(filter(lambda s: s.expected, self.solutions))
        assert len(expected_solutions) == 1
        return expected_solutions[0]


EXAMPLE_PROBLEM_CONFIG_FILE = anchor.SOURCE_ROOT / "data" / "problem.toml"


def load_problem_config(problem_config_file: Path) -> _ProblemConfig:
    return _pydantic.load_model(_ProblemConfig, problem_config_file, strict=True)
