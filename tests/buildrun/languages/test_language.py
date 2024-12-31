from pathlib import Path

import pytest

from cp_problem_maker.buildrun.languages.cpp import Cpp
from cp_problem_maker.buildrun.languages.language import ILanguage


class TestLanguages:
    @pytest.mark.parametrize(
        "file_path, expected_language_type",
        [
            (Path("test.cpp"), Cpp),
            (Path("subdir/test.cxx"), Cpp),
        ],
    )
    def test_detect_language_valid(
        self, file_path: Path, expected_language_type: type[ILanguage]
    ) -> None:
        assert ILanguage.detect_language(file_path) == expected_language_type

    def test_detect_language_valid_user_defined(self) -> None:
        class DummyLanguage(ILanguage):
            @staticmethod
            def get_name() -> str:
                return "DummyLanguage"

            @staticmethod
            def get_extensions() -> list[str]:
                return [".__my_extension__"]

        assert ILanguage.detect_language(Path("test.__my_extension__")) == DummyLanguage

    def test_detect_language_invalid(self) -> None:
        with pytest.raises(ValueError):
            ILanguage.detect_language(Path("test.__invalid_extension__"))
