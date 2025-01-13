import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest
from pytest_mock import MockerFixture

from cp_problem_maker import subcommands


@pytest.fixture(scope="function")
def cpp_file() -> Generator[Path, Any, None]:
    """Fixture to create a temporary C++ file.

    Yields:
        Generator[Path, Any, None]: Path to the temporary C++ file
    """
    path = Path(tempfile.NamedTemporaryFile(suffix=".cpp", delete=False).name)
    yield path
    path.unlink()


@pytest.fixture(scope="function")
def py_file() -> Generator[Path, Any, None]:
    """Fixture to create a temporary Python file.

    Yields:
        Generator[Path, Any, None]: Path to the temporary Python file
    """
    path = Path(tempfile.NamedTemporaryFile(suffix=".py", delete=False).name)
    yield path
    path.unlink()


@pytest.fixture(scope="function")
def project_root(mocker: MockerFixture) -> Generator[Path, Any, None]:
    """Fixture to create a temporary project directory.

    Yields:
        Generator[Path, Any, None]: Path to the temporary project directory
    """
    with tempfile.TemporaryDirectory() as dirname:
        root = Path(dirname)
        subcommands.InitCommand.init(path=root, search_root=False)
        yield root
