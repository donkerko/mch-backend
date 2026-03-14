from pathlib import Path
import os


def get_onedrive_root() -> Path:
    env_value = os.environ.get("ONEDRIVE")
    if env_value:
        return Path(env_value)

    raise RuntimeError("ONEDRIVE environment variable not found.")

def get_backend_root() -> Path:
    return get_onedrive_root() / "backend"


def get_global_log_dir() -> Path:
    return get_backend_root() / "logs"