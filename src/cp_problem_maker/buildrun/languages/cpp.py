import subprocess
from pathlib import Path

from cp_problem_maker.buildrun.languages.language import CompileResult, ILanguage
from cp_problem_maker.config import tool_config
from cp_problem_maker.logging.setup import get_logger

logger = get_logger(__name__)


class Cpp(ILanguage):
    def __init__(self, cpp_config: tool_config._Cpp) -> None:
        super().__init__()
        self.cpp_config = cpp_config
        # Cache the compilation result
        self.compile_cache: dict[Path, CompileResult] = {}

    @classmethod
    def get_name(cls) -> str:
        return "C++"

    @classmethod
    def get_extensions(cls) -> list[str]:
        return [".cpp", ".cc", ".cxx", ".c++"]

    @staticmethod
    def _exec_file(file_path: Path) -> Path:
        return file_path.with_suffix("")

    def compile(self, file_path: Path) -> CompileResult:
        file_path = file_path.resolve()

        # Check cache
        if file_path in self.compile_cache:
            return self.compile_cache[file_path]

        exec_file = Cpp._exec_file(file_path)
        cmd = [
            self.cpp_config.compiler,
            *self.cpp_config.flags,
            "-o",
            str(exec_file),
            str(file_path),
        ]
        logger.debug("Running command: %s", cmd)
        subprocess.run(cmd)
        result = CompileResult(
            language=Cpp,
            exec_cmd=[str(exec_file.resolve())],
        )

        # Update cache
        self.compile_cache[file_path] = result

        return result


class SolverCpp(Cpp):
    def __init__(self, cpp_config: tool_config._Cpp) -> None:
        super().__init__(cpp_config)
        solver_config = self.cpp_config.solver
        if solver_config is not None:
            compiler = solver_config.compiler
            flags = solver_config.flags
            if compiler is not None:
                self.cpp_config.compiler = compiler
            if flags is not None:
                self.cpp_config.flags = flags
