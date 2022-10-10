from pathlib import Path


def ensure_dir(path: Path):
    if not path.is_dir():
        raise FileNotFoundError(f"Directory '{path}' not found.")

def ensure_file(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"File '{path}' not found.")

def ensure_not_exists(path: Path):
    if path.exists():
        raise FileExistsError(f"File/Directory '{path}' already exists.")

def ensure_empty_dir(path: Path):
    if not path.is_dir() or [*path.iterdir()]:
        raise FileExistsError(f"Directory '{path}' is not empty.")