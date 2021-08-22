import os
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture(name='tmp_path')
def tmp_path_fixture(tmp_path: Path) -> Iterator[Path]:
    cwd = os.getcwd()

    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)
