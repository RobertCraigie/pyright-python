import os
import sys
import logging
import subprocess
from typing import List, NoReturn, Union, Any

from . import __pyright_version__, node
from .utils import env_to_bool


__all__ = (
    'run',
    'main',
)

log: logging.Logger = logging.getLogger(__name__)


def main(args: List[str], **kwargs: Any) -> int:
    return run(*args, **kwargs).returncode


def run(
    *args: str, **kwargs: Any
) -> Union['subprocess.CompletedProcess[bytes]', 'subprocess.CompletedProcess[str]']:
    version = os.environ.get('PYRIGHT_PYTHON_FORCE_VERSION', __pyright_version__)
    if version == 'latest':
        version = node.latest('pyright')

    npx = node.version('npx')
    if npx[0] >= 7:
        pre_args = ['--yes']

        if not env_to_bool('PYRIGHT_PYTHON_VERBOSE', default=False):
            pre_args.insert(0, '--silent')
    else:
        pre_args = []

    if args and pre_args:
        pre_args = (*pre_args, '--')

    return node.run('npx', *pre_args, f'pyright@{version}', *args, **kwargs)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
