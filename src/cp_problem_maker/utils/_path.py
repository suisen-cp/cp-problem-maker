from pathlib import Path


def search_root(path: Path, marker: str) -> Path:
    """Search for the root directory of a project.

    Args:
        path (Path): Path to start the search from
        marker (str): Marker to search for
    Returns:
        Path: Root directory of the project
    """
    while True:
        if (path / marker).exists():
            return path
        if path == path.parent:
            raise FileNotFoundError(f"Could not find {marker}")
        path = path.parent
