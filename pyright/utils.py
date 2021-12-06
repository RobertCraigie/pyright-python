import os
import sys
import tempfile
from getpass import getuser
from pathlib import Path
from typing import Union


def get_env_dir() -> Path:
    """Returns the directory that contains the nodeenv"""
    env_dir = os.environ.get('PYRIGHT_PYTHON_ENV_DIR')
    if env_dir is not None:
        return Path(env_dir)

    try:
        suffix = f'.{getuser()}'
    except Exception:
        suffix = ''

    return Path(tempfile.gettempdir()) / f'pyright-python{suffix}' / 'env'


def env_to_bool(key: str, *, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default

    return value.lower() in {'1', 't', 'on', 'true'}


def maybe_decode(data: Union[str, bytes]) -> str:
    if isinstance(data, bytes):
        return data.decode(sys.getdefaultencoding())

    return data
