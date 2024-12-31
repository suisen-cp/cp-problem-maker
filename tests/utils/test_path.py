from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

import pytest

from cp_problem_maker.utils._path import search_root


@pytest.mark.parametrize(
    "marker, marker_type", [("pyproject.toml", "file"), (".git", "folder")]
)
def test_search_root(marker: str, marker_type: Literal["file", "folder"]) -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        if marker_type == "file":
            (root / marker).touch()
        else:
            (root / marker).mkdir()
        cwd = root / "AAA/BBB/CCC/DDD"
        cwd.mkdir(parents=True)
        assert search_root(cwd, marker) == root


def test_search_root_not_found() -> None:
    with TemporaryDirectory() as tmpdir:
        cwd = Path(tmpdir) / "AAA/BBB/CCC/DDD"
        cwd.mkdir(parents=True)
        with pytest.raises(FileNotFoundError):
            search_root(cwd, "DUMMY" * 10)
