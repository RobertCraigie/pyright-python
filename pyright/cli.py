import os
import sys
import logging
import subprocess
from typing import List, NoReturn, Union, Any, Tuple

from . import node
from .utils import env_to_bool


__all__ = (
    'run',
    'main',
)

log: logging.Logger = logging.getLogger(__name__)


def main(args: List[str], **kwargs: Any) -> int:
    return run(*args, **kwargs).returncode


def build_cmd(
    *args: str, pyright_version: str, npx_version: Tuple[int, ...]
) -> List[str]:
    if npx_version[0] >= 7:
        pre_args = ['--yes']

        if not env_to_bool('PYRIGHT_PYTHON_VERBOSE', default=False):
            pre_args.insert(0, '--silent')
    else:
        pre_args = []

    return ['npx', *pre_args, f'pyright@{pyright_version}', *args]


def run(
    *args: str, **kwargs: Any
) -> Union['subprocess.CompletedProcess[bytes]', 'subprocess.CompletedProcess[str]']:
    version = os.environ.get('PYRIGHT_PYTHON_FORCE_VERSION')
    if version is None:
        version = node.latest('pyright')

    npx = node.version('npx')

    target, *cmd_args = build_cmd(*args, pyright_version=version, npx_version=npx)
    assert target == 'npx'

    return node.run(target, *cmd_args, **kwargs)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
