import os
from typing import Iterator
from pathlib import Path

import pytest

from pyright import node


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
    return str(
        node._ensure_available('node').path  # pyright: ignore[reportPrivateUsage]
    )


@pytest.fixture(autouse=True)
def temp_env() -> Iterator[None]:
    old = os.environ.copy()

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)
