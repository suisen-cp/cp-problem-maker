from enum import Enum
import logging
from pathlib import Path
from subprocess import check_call
from typing import List

from cp_problem_maker.config import Config
from cp_problem_maker.judge import JudgeStatus, UnexpectedRuntimeError, UnexpectedTimeLimitExceeded, judge
from cp_problem_maker.util import pathlib_util

logger: logging.Logger = logging.getLogger(__name__)


class UnknownGeneratorTypeError(Exception):
    def __init__(self, generator_file: Path):
        self.message = f'Generator files must be named as "*.cpp" or ".in", but "{generator_file}" does not match the pattern.'
        super().__init__(self.message)


class GeneratorType(Enum):
    EXAMPLE = 0
    CPP = 1

    @staticmethod
    def from_file(generator_file: Path) -> 'GeneratorType':
        ext = generator_file.suffix
        if ext == '.in':
            return GeneratorType.EXAMPLE
        elif ext == '.cpp':
            return GeneratorType.CPP
        else:
            raise UnknownGeneratorTypeError(generator_file)


class TestCase:
    def __init__(self, generator_file: Path, case_no: int) -> None:
        self.generator_file = generator_file
        self.case_no = case_no
    
        self.case_name = f'{self.generator_file.with_suffix("").name}'
        self.case_name_with_no = f'{self.case_name}_{self.case_no:02}'

        self.generator_type = GeneratorType.from_file(self.generator_file)

        self.input_file_name = f'{self.case_name_with_no}.in'
        self.output_file_name = f'{self.case_name_with_no}.out'

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        pathlib_util.ensure_file(self.generator_file)

    def _generate_input_cmd(self) -> List[str]:
        exe_file = self.generator_file.with_suffix('')
        if self.generator_type == GeneratorType.EXAMPLE:
            return [
                'cat',
                f'{self.generator_file.with_name(self.input_file_name)}'
            ]
        elif self.generator_type == GeneratorType.CPP:
            return [
                f'{exe_file}',
                f'{self.case_no}'
            ]
        else:
            raise ValueError(f'{self.generator_type} is not GeneratorType.')

    def generate_input(self, input_folder: Path, *, parents=False, exist_ok=False) -> None:
        if not parents:
            pathlib_util.ensure_dir(input_folder)
        else:
            input_folder.mkdir(parents=True, exist_ok=True)
        input_file = input_folder / self.input_file_name
        if not exist_ok:
            pathlib_util.ensure_not_exists(input_file)
        logger.info(f"generating input: {input_file.name}...")
        check_call(self._generate_input_cmd(), stdout=open(input_file, mode='w'))

    def _verify_cmd(self, verifier_file: Path) -> List[str]:
        verifier_exe_file = verifier_file.with_suffix('')
        pathlib_util.ensure_file(verifier_exe_file)
        return [
            f'{verifier_exe_file}'
        ]

    def verify_input(self, *, input_folder: Path, verifier_file: Path) -> None:
        input_file = input_folder / self.input_file_name
        pathlib_util.ensure_file(input_file)
        logger.info(f"verifying input: {self.input_file_name}...")
        check_call(self._verify_cmd(verifier_file), stdin=open(input_file))

    def _generate_output_cmd(self, solution_file: Path) -> List[str]:
        return [
            f'{solution_file.with_suffix("")}'
        ]

    def generate_output(self, *, input_folder: Path, output_folder: Path, solution_file: Path, config: Config, parents=False, exist_ok=False) -> None:
        input_file = input_folder / self.input_file_name
        output_file = output_folder / self.output_file_name
        logger.info(f'generating output: {self.input_file_name}...')
        result = judge(
            input_file=input_file,
            output_file=output_file,
            solution_file=solution_file,
            config=config,
            parents=parents,
            exist_ok=exist_ok
        )
        if result.status == JudgeStatus.AC:
            logger.info(f'  result  : SUCCESS')
            logger.info(f'  time    : {result.elapsed_ms} ms')
        elif result.status == JudgeStatus.RE:
            logger.info(f'  result  : FAIL')
            logger.info(f'  cause   ; RE')
            logger.info(f'  time    : {result.elapsed_ms} ms')
            raise UnexpectedRuntimeError()
        elif result.status == JudgeStatus.TLE:
            logger.info(f'  result  : FAIL')
            logger.info(f'  cause   ; TLE')
            logger.info(f'  time    : {result.elapsed_ms} ms')
            raise UnexpectedTimeLimitExceeded()

