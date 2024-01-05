from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import re
from subprocess import check_call
from typing import List
import textwrap

from cp_problem_maker.config import Config
from cp_problem_maker.judge import JudgeStatus, UnexpectedRuntimeError, UnexpectedTimeLimitExceeded, judge
from cp_problem_maker.util import pathlib_util

logger: logging.Logger = logging.getLogger(__name__)

# available suffixes for raw input files
SUFFIX_HAND = [
    '.in',
    '.txt',
]

# available suffixed for C++ generator files
SUFFIX_CPP = [
    '.cpp',
    '.cc',
]

class UnknownGeneratorTypeError(Exception):
    def __init__(self, generator_file: Path):
        self.message = textwrap.dedent(f"""
            Generator file "{generator_file}" does not match any of the patterns below.
            1. "*.cpp" or ".cc": for C++ generator files
            2. "*.in" or ".txt": for raw input files
        """).strip()
        super().__init__(self.message)


class GeneratorType(Enum):
    # raw input files
    RAW = 0
    # C++ generator files
    CPP = 1

    @staticmethod
    def from_file(generator_file: Path) -> 'GeneratorType':
        # case insensitive
        ext = generator_file.suffix.lower()
        if ext in SUFFIX_HAND:
            return GeneratorType.RAW
        elif ext in SUFFIX_CPP:
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

    @staticmethod
    def get_testcase_info(f: Path):
        @dataclass
        class TestCaseInfo:
            case_name: str
            case_no: int
            is_input: bool
        
        if f.is_dir():
            return None
        
        matched = re.fullmatch(r'(?P<name>.+)_(?P<num>[0-9]{2})(?P<suffix>\..+)', f.name)

        if matched is None:
            return None
        
        case_name = matched.group('name')
        case_no = int(matched.group('num'))
        suffix = matched.group('suffix')

        if suffix == '.in':
            is_input = True
        elif suffix == '.out':
            is_input = False
        else:
            return None

        return TestCaseInfo(
            case_name=case_name,
            case_no=case_no,
            is_input=is_input
        )

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        pathlib_util.ensure_file(self.generator_file)

    def _generate_input_cmd(self) -> List[str]:
        exe_file = self.generator_file.with_suffix('')
        if self.generator_type == GeneratorType.RAW:
            return [
                'cat',
                f'{self.generator_file.with_name(self.input_file_name).with_suffix(self.generator_file.suffix)}'
            ]
        elif self.generator_type == GeneratorType.CPP:
            seed = hash(f'{exe_file}_{self.case_no}'.encode()) % (2 ** 31)
            return [
                f'{exe_file}',
                f'{self.case_no}',
                f'{seed}'
            ]
        else:
            raise ValueError(f'{self.generator_type} is not an instance of GeneratorType.')

    def generate_input(self, input_folder: Path, *, parents=False, exist_ok=False) -> None:
        if not parents:
            pathlib_util.ensure_dir(input_folder)
        else:
            input_folder.mkdir(parents=True, exist_ok=True)
        input_file = input_folder / self.input_file_name
        if not exist_ok:
            pathlib_util.ensure_not_exists(input_file)
        logger.info(f"generating input: {input_file.name}...")
        with input_file.open(mode='w') as inf:
            check_call(self._generate_input_cmd(), stdout=inf)

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
        with input_file.open() as inf:
            check_call(self._verify_cmd(verifier_file), stdin=inf)

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

