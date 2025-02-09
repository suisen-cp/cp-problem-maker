from pathlib import Path

from cp_problem_maker.buildrun.languages.language import CompileResult, ILanguage
from cp_problem_maker.config import tool_config


class Python(ILanguage):
    def __init__(self, python_config: tool_config._Python) -> None:
        super().__init__()
        self.python_config = python_config.model_copy(deep=True)

    @classmethod
    def get_name(cls) -> str:
        return "Python"

    @classmethod
    def get_extensions(cls) -> list[str]:
        return [".py"]

    def compile(self, file_path: Path) -> CompileResult:
        return CompileResult(
            language=Python,
            exec_cmd=[self.python_config.python, str(file_path.resolve())],
        )
