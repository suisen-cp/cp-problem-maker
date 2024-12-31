from pathlib import Path

from cp_problem_maker.buildrun.languages.language import CompileResult, ILanguage


class TextCat(ILanguage):
    @classmethod
    def get_name(cls) -> str:
        return "Text (cat)"

    @classmethod
    def get_extensions(cls) -> list[str]:
        return [".txt", ".in"]

    def compile(self, file_path: Path) -> CompileResult:
        return CompileResult(
            language=TextCat,
            exec_cmd=["cat", str(file_path.resolve())],
        )
