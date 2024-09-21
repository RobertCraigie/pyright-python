import os
import sys
import subprocess
from typing import TYPE_CHECKING, Tuple
from pathlib import Path
from unittest import mock

import pytest
from pytest_subprocess import FakeProcess

import pyright
import pyright.node
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
    node: str,
    fake_process: FakeProcess,
    output: bytes,
    version: Tuple[int, ...],
) -> None:
    fake_process.register_subprocess(  # pyright: ignore[reportUnknownMemberType]
        [node, '--version'], stdout=output
    )
    assert pyright.node.version('node') == version


def test_target_version_not_found(
    node: str,
    fake_process: FakeProcess,
    capsys: 'CaptureFixture[str]',
) -> None:
    fake_process.register_subprocess(  # pyright: ignore[reportUnknownMemberType]
        [node, '--version'], stdout='hello world'
    )

    with pytest.raises(pyright.errors.VersionCheckFailed) as exc:
        pyright.node.version('node')

    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'hello world\n'
    assert exc.match('Could not find version from `node --version`, see output above')


def test_run_env_argument(tmp_path: Path) -> None:
    """Ensure the `run()` function can accept an `env` argument."""
    tmp_path.joinpath('test.js').write_text('console.log(process.env.MY_ENV_VAR)')
    proc = pyright.node.run(
        'node',
        'test.js',
        env={**os.environ, 'MY_ENV_VAR': 'hello!'},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.returncode == 0
    assert maybe_decode(proc.stdout) == 'hello!\n'


@mock.patch('pyright.node.NODE_VERSION', '13.1.0')
@mock.patch('pyright.node.USE_GLOBAL_NODE', False)
@mock.patch('pyright.node.USE_NODEJS_WHEEL', False)
def test_node_version_env() -> None:
    """Ensure the custom version is respected."""
    proc = pyright.node.run(
        'node',
        '--version',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.returncode == 0
    assert maybe_decode(proc.stdout).strip() == 'v13.1.0'


@mock.patch('pyright.node.USE_GLOBAL_NODE', False)
@mock.patch('pyright.node.USE_NODEJS_WHEEL', False)
@mock.patch('pyright.node.NODE_VERSION', None)
@mock.patch('pyright.node.BINARIES_DIR', pyright.node.BINARIES_DIR.joinpath('empty'))
def test_nodeenv_flaky_error(fake_process: FakeProcess) -> None:
    """A helpful error is raised when nodeenv fails."""
    fake_process.register_subprocess(  # pyright: ignore[reportUnknownMemberType]
        [sys.executable, '-m', 'nodeenv', str(pyright.node.ENV_DIR)],
        stdout='this thing is flaky',
        returncode=1,
    )

    with pytest.raises(RuntimeError, match=r'install pyright\[nodejs\]'):
        pyright.node.run(
            'node',
            '--version',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


def test_update_path_env(tmp_path: Path) -> None:
    """The _update_path_env() function correctly appends the target binary path to the PATH environment variable"""
    target = tmp_path / 'bin'
    target.mkdir()

    sep = os.pathsep

    # known PATH separators - please update if need be
    assert sep in {':', ';'}

    # no env
    path = pyright.node._update_path_env(env=None, target_bin=target)
    assert path.startswith(f'{target.absolute()}{sep}')

    # env without PATH
    path = pyright.node._update_path_env(
        env={'FOO': 'bar'},
        target_bin=target,
    )
    assert path.startswith(f'{target.absolute()}{sep}')

    # env with empty PATH
    path = pyright.node._update_path_env(
        env={'PATH': ''},
        target_bin=target,
    )
    assert path.startswith(f'{target.absolute()}{sep}')

    # env with set PATH without the separator postfix
    path = pyright.node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # env with set PATH with the separator as a prefix
    path = pyright.node._update_path_env(
        env={'PATH': f'{sep}/foo'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # returned env included non PATH environment variables
    path = pyright.node._update_path_env(
        env={'PATH': '/foo', 'FOO': 'bar'},
        target_bin=target,
    )
    assert path == f'{target.absolute()}{sep}/foo'

    # accepts a custom path separator
    path = pyright.node._update_path_env(
        env={'PATH': '/foo'},
        target_bin=target,
        sep='---',
    )
    assert path == f'{target.absolute()}---/foo'
