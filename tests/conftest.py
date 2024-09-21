import os
from typing import Iterator
from pathlib import Path

import pytest
import nodejs_wheel


@pytest.fixture(name='tmp_path')
def tmp_path_fixture(tmp_path: Path) -> Iterator[Path]:
    cwd = os.getcwd()

    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture(name='node', scope='session')
def node_fixture() -> str:
    if os.name == 'nt':
        return str(Path(nodejs_wheel.__file__).parent / 'node.exe')

    return str(Path(nodejs_wheel.__file__).parent / 'bin' / 'node')


@pytest.fixture(autouse=True)
def temp_env() -> Iterator[None]:
    old = os.environ.copy()

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)
