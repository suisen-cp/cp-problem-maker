import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator


@contextmanager
def temp_files(
    num_files: int = 3,
    suffix: str | None | list[str] = None,
) -> Generator[tuple[IO[str], ...], None, None]:
    """Create temporary files for stdin, stdout, and stderr.

    Args:
        num_files (int, optional): Number of files to create. Defaults to 3.

    Yields:
        Generator[tuple[TextIOWrapper, ...], None, None]: Tuple of temporary files
    """
    tempdir = tempfile.TemporaryDirectory()
    if not isinstance(suffix, list):
        suffix = [suffix] * num_files  # type: ignore
    try:
        temp_files: list[IO[str]] = []
        for i in range(num_files):
            temp_file = Path(tempdir.name) / f"{i}"
            if suffix[i] is not None:
                temp_file = temp_file.with_suffix(suffix[i])
            temp_files.append(temp_file.open("w+"))
        yield tuple(temp_files)
    finally:
        tempdir.cleanup()
