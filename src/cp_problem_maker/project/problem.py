from pathlib import Path

from cp_problem_maker.config import problem_config, tool_config
from cp_problem_maker.utils import _path

LOCAL_CONFIG_DIR_NAME = ".cp_problem_maker"
LOCAL_CONFIG_FILE_NAME = "config.toml"


def _local_config_dir(root: Path) -> Path:
    return root / LOCAL_CONFIG_DIR_NAME


def _local_config_file(root: Path) -> Path:
    return _local_config_dir(root) / LOCAL_CONFIG_FILE_NAME


class Problem:
    def __init__(
        self,
        *,
        root: Path,
        path_config: tool_config._Path,
        default_lang: tool_config._DefaultLanguage,
    ):
        self.root = root
        self.path_config = path_config
        self.default_lang: tool_config._DefaultLanguage = default_lang

    @staticmethod
    def search_problem_root(path: Path | None = None) -> Path:
        """Search for the root directory of a problem.

        Args:
            path (Path | None):
                Path to start the search from.
                Defaults to the current working directory.
        Returns:
            Path:
                Root directory of the problem
        Raises:
            FileNotFoundError:
                If the root directory of the problem could not be found.
        """
        if path is None:
            path = Path.cwd()
        return _path.search_root(path, LOCAL_CONFIG_DIR_NAME)

    def _default_source_suffix(self) -> str:
        """Get the default source file suffix based on the default language."""
        match self.default_lang:
            case "C++":
                return ".cpp"
            case "Python":
                return ".py"
            case _:
                raise ValueError(f"Unsupported language {self.default_lang}")

    @property
    def config_dir(self) -> Path:
        return _local_config_dir(self.root)

    @property
    def local_config_file(self) -> Path:
        return _local_config_file(self.root)

    @property
    def problem_config_file(self) -> Path:
        return self.root / self.path_config.problem_config

    @property
    def checker_file(self) -> Path:
        checker_file = self.root / Path(self.path_config.checker)
        if checker_file.suffix:
            return checker_file
        return checker_file.with_suffix(self._default_source_suffix())

    @property
    def verifier_file(self) -> Path:
        verifier_file = self.root / Path(self.path_config.verifier)
        if verifier_file.suffix:
            return verifier_file
        return verifier_file.with_suffix(self._default_source_suffix())

    @property
    def generators_dir(self) -> Path:
        return self.root / self.path_config.generators

    @property
    def solutions_dir(self) -> Path:
        return self.root / self.path_config.solutions

    @property
    def inputs_dir(self) -> Path:
        return self.root / self.path_config.inputs

    @property
    def outputs_dir(self) -> Path:
        return self.root / self.path_config.outputs

    @property
    def params_file(self) -> Path:
        params_file = self.root / Path(self.path_config.params)
        if params_file.suffix:
            return params_file
        match self.default_lang:
            case "C++":
                suffix = ".h"
            case "Python":
                suffix = ".py"
            case _:
                raise ValueError(f"Unsupported language {self.default_lang}")
        return params_file.with_suffix(suffix)

    @staticmethod
    def testcase_file_stem(test_name: str, test_id: int) -> str:
        return f"{Path(test_name).stem}_{test_id:02d}"

    @staticmethod
    def input_file(inputs_dir: Path, test_name: str, test_id: int) -> Path:
        return (
            inputs_dir / Problem.testcase_file_stem(test_name, test_id)
        ).with_suffix(".in")

    @staticmethod
    def output_file(outputs_dir: Path, test_name: str, test_id: int) -> Path:
        return (
            outputs_dir / Problem.testcase_file_stem(test_name, test_id)
        ).with_suffix(".out")

    def init_problem(self) -> None:
        """Initialize the problem directory structure."""
        self.root.mkdir(exist_ok=True)

        new_files: list[Path] = []
        new_dirs: list[Path] = []

        new_files.append(self.local_config_file)
        new_files.append(self.problem_config_file)
        new_files.append(self.checker_file)
        new_files.append(self.verifier_file)
        new_files.append(self.params_file)

        new_dirs.append(self.generators_dir)
        new_dirs.append(self.solutions_dir)
        new_dirs.append(self.inputs_dir)
        new_dirs.append(self.outputs_dir)
        new_dirs.append(self.config_dir)
        new_dirs.extend([f.parent for f in new_files])

        existing_dirs = [f for f in new_files if f.exists() and f.is_dir()]
        existing_files = [d for d in new_dirs if d.exists() and d.is_file()]

        if existing_files or existing_dirs:
            raise FileExistsError(
                f"Files already exist: {existing_files + existing_dirs}"
            )

        for d in new_dirs:
            d.mkdir(parents=True, exist_ok=True)
        for f in new_files:
            f.touch(exist_ok=True)

        if self.problem_config_file.stat().st_size == 0:
            self.problem_config_file.write_text(
                problem_config.EXAMPLE_PROBLEM_CONFIG_FILE.read_text()
            )


class ProblemWithConfig:
    def __init__(self, root: Path | None, *, search_root: bool) -> None:
        if root is None:
            root = Path.cwd()
        if search_root:
            root = Problem.search_problem_root(root)

        self.config = tool_config.load_local_config(_local_config_file(root))
        self.problem = Problem(
            root=root,
            path_config=self.config.path,
            default_lang=self.config.language.default,
        )
        if self.problem.local_config_file.exists():
            self.problem_config = problem_config.load_problem_config(
                self.problem.problem_config_file
            )
