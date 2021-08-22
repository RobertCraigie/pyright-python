import os
import sys
import logging
import subprocess
from typing import List, NoReturn, Union, Any

from . import node


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
    version = os.environ.get('PYRIGHT_PYTHON_FORCE_VERSION')
    if version is None:
        version = node.latest('pyright')

    npx = node.version('npx')
    if npx[0] >= 7:
        pre_args = ['--yes']
    else:
        pre_args = []

    return node.run('npx', *pre_args, f'pyright@{version}', '--', *args, **kwargs)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
