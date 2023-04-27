import os
from pathlib import Path
from typing import Iterator

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


@pytest.fixture(name='npx', scope='session')
def npx_fixture() -> str:
    return str(node._ensure_available('npx').path)  # pyright: ignore[reportPrivateUsage]


@pytest.fixture(autouse=True)
def temp_env() -> Iterator[None]:
    old = os.environ.copy()

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)
