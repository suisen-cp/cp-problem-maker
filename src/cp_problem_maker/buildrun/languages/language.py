import abc
from pathlib import Path

from pydantic import BaseModel


class CompileResult(BaseModel):
    language: "type[ILanguage]"
    """Language of the file"""
    exec_cmd: list[str]
    """Command to execute the compiled file"""


class ILanguage(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Get the name of the language

        Returns:
            str: Name of the language
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_extensions(cls) -> list[str]:
        """Get the extensions of the language

        Returns:
            list[str]: List of extensions
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def compile(self, file_path: Path) -> CompileResult:
        """Compile the file"""
        raise NotImplementedError()

    @staticmethod
    def detect_language(file_path: Path) -> "type[ILanguage]":
        """Detect the language of the file

        Args:
            file_path (Path): Path to the file
        Returns:
            type[ILanguage]: ILanguage class
        Raises:
            ValueError: If the language is not supported
        """
        for language in ILanguage.__subclasses__():
            if file_path.suffix in language.get_extensions():
                return language
        else:
            raise ValueError(f"Unsupported language for file {file_path}")
