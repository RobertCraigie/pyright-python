import os
import sys
import logging
from typing import List, NoReturn

from . import node


log: logging.Logger = logging.getLogger(__name__)
PYRIGHT_VERSION: str = os.environ.get('PYRIGHT_PYTHON_VERSION', '1.1.150')


def main(args: List[str]) -> int:
    return node.run('npx', '--yes', f'pyright@{PYRIGHT_VERSION}', *args)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
