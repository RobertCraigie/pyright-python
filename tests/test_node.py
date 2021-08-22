from typing import Tuple, TYPE_CHECKING

import pytest
from pytest_subprocess import FakeProcess

import pyright
from pyright import node


if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


# TODO: test binary resolution

NPX = str(node._ensure_available('npx').path)  # pyright: reportPrivateUsage=false


@pytest.mark.parametrize(
    'version,output',
    [
        [(10, 100, 100), '10.100.100'],
        [(7, 1, 4), b'7.1.4'],
        [(1, 0, 0), b'1.0.0'],
        [(7, 6, 7), b'7.6.7'],
        [
            (7, 1, 3),
            b'(node:3388) ExperimentalWarning: The fs.promises API is experimental\n7.1.3',
        ],
    ],
)
def test_target_version(
    fake_process: FakeProcess, output: bytes, version: Tuple[int, ...]
) -> None:
    fake_process.register_subprocess(
        [NPX, "--version"], stdout=output
    )  # pyright: reportUnknownMemberType=false
    assert node.version('npx') == version


def test_target_version_not_found(
    fake_process: FakeProcess, capsys: 'CaptureFixture[str]'
) -> None:
    fake_process.register_subprocess(
        [NPX, "--version"], stdout='hello world'
    )  # pyright: reportUnknownMemberType=false

    with pytest.raises(pyright.errors.VersionCheckFailed) as exc:
        node.version('npx')

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'hello world\n'
    assert exc.match('Could not find version from `npx --version`, see output above')
