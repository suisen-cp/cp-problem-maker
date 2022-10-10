import logging
from os import getcwd
from pathlib import Path

from cp_problem_maker.util.pathlib_util import ensure_empty_dir

logger: logging.Logger = logging.getLogger(__name__)


class Problem:
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

    def create_problem(self) -> None:
        logger.info("creating problem...")

        self.problem_folder.mkdir(parents=True, exist_ok=True)

        ensure_empty_dir(self.problem_folder)

        self.in_folder.mkdir(exist_ok=True)
        self.out_folder.mkdir(exist_ok=True)
        self.gen_folder.mkdir(exist_ok=True)
        self.include_folder.mkdir(exist_ok=True)
        self.solutions_folder.mkdir(exist_ok=True)

        self.solution_file.touch(exist_ok=True)
        self.checker_file.touch(exist_ok=True)
        self.verifier_file.touch(exist_ok=True)
        self.config_file.touch(exist_ok=True)
        self.task_file.touch(exist_ok=True)
