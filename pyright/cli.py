import sys
import logging
from typing import List, NoReturn

from . import node
from .utils import config


log: logging.Logger = logging.getLogger(__name__)


def main(args: List[str]) -> int:
    return node.run('npx', '--yes', f'pyright@{config.pyright_version}', *args)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
