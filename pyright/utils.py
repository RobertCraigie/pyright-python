import os
import tempfile
from pathlib import Path

from . import __version__


def get_env_dir() -> Path:
    """Returns the directory that contains the nodeenv"""
    env_dir = os.environ.get('PYRIGHT_PYTHON_ENV_DIR')
    if env_dir is not None:
        return Path(env_dir)

    return Path(tempfile.gettempdir()) / 'pyright-prisma' / __version__ / 'env'
