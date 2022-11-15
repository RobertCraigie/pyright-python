import os
import subprocess
from typing import Tuple, TYPE_CHECKING
from pathlib import Path

import pytest
from pytest_subprocess import FakeProcess

import pyright
from pyright import node
from pyright.utils import maybe_decode


if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


# TODO: test binary resolution


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
    npx: str,
    fake_process: FakeProcess,
    output: bytes,
    version: Tuple[int, ...],
) -> None:
    fake_process.register_subprocess(
        [npx, "--version"], stdout=output
    )  # pyright: reportUnknownMemberType=false
    assert node.version('npx') == version


def test_target_version_not_found(
    npx: str,
    fake_process: FakeProcess,
    capsys: 'CaptureFixture[str]',
) -> None:
    fake_process.register_subprocess(
        [npx, "--version"], stdout='hello world'
    )  # pyright: reportUnknownMemberType=false

    with pytest.raises(pyright.errors.VersionCheckFailed) as exc:
        node.version('npx')

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'hello world\n'
    assert exc.match('Could not find version from `npx --version`, see output above')


def test_run_env_argument(tmp_path: Path) -> None:
    """Ensure the `run()` function can accept an `env` argument."""
    tmp_path.joinpath('test.js').write_text("console.log(process.env.MY_ENV_VAR)")
    proc = node.run(
        'node',
        'test.js',
        env={**os.environ, 'MY_ENV_VAR': 'hello!'},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.returncode == 0
    assert maybe_decode(proc.stdout) == 'hello!\n'


def test_update_path_env(tmp_path: Path) -> None:
    """The _update_path_env() function correctly appends the target binary path to the PATH environment variable"""
    target = tmp_path / 'bin'
    target.mkdir()

    sep = os.pathsep

    # known PATH separators - please update if need be
    assert sep in {':', ';'}

    # no env
    path = node._update_path_env(env=None, target_bin=target)
    assert path.startswith(f'{target.absolute()}{sep}')

    # env without PATH
    path = node._update_path_env(
        env={'FOO': 'bar'},
        target_bin=target,
    )
    assert path.startswith(f'{target.absolute()}{sep}')

    # env with empty PATH
    path = node._update_path_env(
        env={'PATH': ''},
        target_bin=target,
    )
    assert path.startswith(f'{target.absolute()}{sep}')

    # env with set PATH without the separator postfix
    path = node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # env with set PATH with the separator as a prefix
    path = node._update_path_env(
        env={'PATH': f'{sep}/foo'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # returned env included non PATH environment variables
    path = node._update_path_env(
        env={'PATH': '/foo', 'FOO': 'bar'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # accepts a custom path separator
    path = node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
        sep='---',
    )
    assert path == f'{target.absolute()}---/foo'
