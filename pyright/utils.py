import os
import tempfile
from pathlib import Path


def get_env_dir() -> Path:
    """Returns the directory that contains the nodeenv"""
    env_dir = os.environ.get('PYRIGHT_PYTHON_ENV_DIR')
    if env_dir is not None:
        return Path(env_dir)

    return Path(tempfile.gettempdir()) / 'pyright-prisma' / 'env'


def env_to_bool(key: str, *, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default

    return value.lower() in {'1', 't', 'on', 'true'}
