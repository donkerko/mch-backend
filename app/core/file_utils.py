from pathlib import Path
import shutil


def ensure_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_file(src: Path, dst: Path, overwrite: bool = False) -> Path:
    src = Path(src)
    dst = Path(dst)

    if dst.exists() and not overwrite:
        return dst

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst