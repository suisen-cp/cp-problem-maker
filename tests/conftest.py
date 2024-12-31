import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest


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
