import logging
from os import getcwd
from pathlib import Path
import shutil

from cp_problem_maker.util.pathlib_util import ensure_empty_dir, ensure_not_exists

logger: logging.Logger = logging.getLogger(__name__)


class Problem:
    TEMPLATES_DIR = Path(__file__).parent.parent / 'template'

    def __init__(self, path: Path) -> None:
        if path.is_absolute():
            self.problem_folder = path.resolve()
        else:
            self.problem_folder = (Path(getcwd()) / path).resolve()
        self.in_folder = self.problem_folder / "in"
        self.out_folder = self.problem_folder / "out"
        self.gen_folder = self.problem_folder / "gen"
        self.solutions_folder = self.problem_folder / "sol"
        self.include_folder = self.problem_folder / "include"
        self.solution_file = self.solutions_folder / "correct.cpp"
        self.checker_file = self.problem_folder / "checker.cpp"
        self.verifier_file = self.problem_folder / "verifier.cpp"
        self.config_file = self.problem_folder / "info.toml"
        self.task_file = self.problem_folder / "task.md"
        self.params_file = self.include_folder / "params.hpp"
        self.compile_config_file = self.problem_folder / "compile_info.toml"

    def create_problem(self) -> None:
        logger.info("creating problem...")

        self.problem_folder.mkdir(parents=True, exist_ok=True)

        ensure_empty_dir(self.problem_folder)

        self.in_folder.mkdir(exist_ok=False)
        self.out_folder.mkdir(exist_ok=False)
        self.gen_folder.mkdir(exist_ok=False)
        self.include_folder.mkdir(exist_ok=False)
        self.solutions_folder.mkdir(exist_ok=False)

        self.solution_file.touch(exist_ok=False)
        self.checker_file.touch(exist_ok=False)
        self.verifier_file.touch(exist_ok=False)
        self.task_file.touch(exist_ok=False)

        ensure_not_exists(self.config_file)
        ensure_not_exists(self.compile_config_file)

        shutil.copy(Problem.TEMPLATES_DIR / 'info.toml', self.config_file)
        shutil.copy(Problem.TEMPLATES_DIR / 'compile_info.toml', self.compile_config_file)
