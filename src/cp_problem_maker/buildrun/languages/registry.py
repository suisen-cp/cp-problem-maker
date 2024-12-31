from pathlib import Path
from typing import overload

from cp_problem_maker.buildrun.languages.cpp import Cpp, SolverCpp
from cp_problem_maker.buildrun.languages.language import ILanguage
from cp_problem_maker.buildrun.languages.python import Python
from cp_problem_maker.buildrun.languages.text_cat import TextCat
from cp_problem_maker.config import tool_config


class LanguageRegistry:
    _instances: dict[type[ILanguage], ILanguage] = {}

    @staticmethod
    def load_config(config: tool_config._Language) -> None:
        LanguageRegistry._instances[Cpp] = Cpp(config.cpp)
        LanguageRegistry._instances[SolverCpp] = SolverCpp(config.cpp)
        LanguageRegistry._instances[Python] = Python(config.python)
        LanguageRegistry._instances[TextCat] = TextCat()

    @overload
    @staticmethod
    def get_languege(obj: type[ILanguage]) -> ILanguage: ...

    @overload
    @staticmethod
    def get_languege(obj: Path) -> ILanguage: ...

    @staticmethod
    def get_languege(obj: type[ILanguage] | Path) -> ILanguage:
        if isinstance(obj, Path):
            obj = ILanguage.detect_language(obj)
        return LanguageRegistry._instances[obj]
