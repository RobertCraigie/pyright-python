from __future__ import annotations

import os
import re
import sys
import json
import platform
import subprocess
from typing import TYPE_CHECKING
from pathlib import Path

from packaging import version

import pyright
from pyright import __pyright_version__
from tests.utils import assert_matches
from pyright.utils import maybe_decode

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


VERSION_REGEX = re.compile(r'pyright (?P<version>\d+\.\d+\.\d+)')


def test_module_invocation() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert proc.returncode == 0
    match = assert_matches(VERSION_REGEX, proc.stdout.decode('utf-8'))
    assert match.group(1) == __pyright_version__


def test_module_invocation_version() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_FORCE_VERSION='1.1.223'),
    )
    assert proc.returncode == 0
    match = assert_matches(VERSION_REGEX, proc.stdout.decode('utf-8'))
    assert match.group(1) == '1.1.223'


def test_module_invocation_latest_version() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_FORCE_VERSION='latest'),
    )
    assert proc.returncode == 0
    match = assert_matches(VERSION_REGEX, proc.stdout.decode('utf-8'))
    assert version.parse(match.group(1)) >= version.parse(__pyright_version__)


def test_module_invocation_pylance_version() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_PYLANCE_VERSION='2023.11.11'),
    )
    assert proc.returncode == 0
    match = assert_matches(VERSION_REGEX, proc.stdout.decode('utf-8'))
    assert match.group(1) == '1.1.334'


def test_module_invocation_pylance_version_latest_prerelease() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_PYLANCE_VERSION='latest-prerelease'),
    )
    assert proc.returncode == 0
    match = assert_matches(VERSION_REGEX, proc.stdout.decode('utf-8'))
    # Can't predict which version of pyright is currently used by pylance. Just
    # ensure that the process ran succesfully and some pyright version appeared
    # in the output.
    assert len(match.groups()) == 1


def test_entry_point() -> None:
    proc = subprocess.run(
        ['pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    match = assert_matches(VERSION_REGEX, output)
    assert match.group(1) == __pyright_version__


def test_long_arguments(tmp_path: Path) -> None:
    """Long arguments (e.g. --outputjson) are passed to the pyright CLI"""
    tmp_path.joinpath('foo.py').write_text('reveal_type(1)')

    result = pyright.run('--outputjson', 'foo.py', stdout=subprocess.PIPE)
    assert result.returncode == 0

    data = json.loads(result.stdout)
    assert data['generalDiagnostics'][0]['message'] == 'Type of "1" is "Literal[1]"'


def test_argument_separator(tmp_path: Path) -> None:
    """Ensure the npx / pyright argument separator correctly separates arguments."""
    tmp_path.joinpath('foo.py').write_text('reveal_type(1)')

    result = pyright.run('foo.py', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert result.returncode == 0

    output = maybe_decode(result.stdout)
    assert 'does not exist' not in output


def test_explicit_version_new_version_warning() -> None:
    """A new version is available warning is emitted explicitly using an older version"""
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_FORCE_VERSION='1.1.222'),
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert 'WARNING: there is a new pyright version available' in output


def test_explicit_latest_no_new_version_warning() -> None:
    """No new version warning is emitted when explicitly setting to `latest`"""
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_FORCE_VERSION='latest'),
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert 'WARNING: there is a new pyright version available' not in output


def test_pylance_version_no_new_version_warning() -> None:
    """No new version warning is emitted when PYRIGHT_PYTHON_PYLANCE_VERSION is set"""
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_PYLANCE_VERSION='2023.11.10'),
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert 'WARNING: there is a new pyright version available' not in output


def test_output_json_no_warning() -> None:
    """If the --outputjson flag is set then no warning is emitted"""
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version', '--outputjson'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(os.environ, PYRIGHT_PYTHON_FORCE_VERSION='1.1.222'),
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert 'WARNING: there is a new pyright version available' not in output


def test_ignore_warnings_config_no_warning() -> None:
    """If the --outputjson flag is set then no warning is emitted"""
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(
            os.environ,
            PYRIGHT_PYTHON_FORCE_VERSION='1.1.222',
            PYRIGHT_PYTHON_IGNORE_WARNINGS='1',
        ),
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert 'WARNING: there is a new pyright version available' not in output


def test_nodeenv() -> None:
    """Ensure nodeenv is successfully downloaded and used"""
    subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
        env=dict(
            os.environ,
            PYRIGHT_PYTHON_GLOBAL_NODE='0',
        ),
    )


def test_user_special_characters() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={
            **os.environ,
            'LOGNAME': 'alice@example.com',
        },
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    assert str(__pyright_version__) in output


def test_package_json_in_parent_dir(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """The CLI can be installed successfully when there is a `package.json` file
    in a parent directory.
    """
    if platform.system() == 'Windows':
        # hack to avoid WinError 206
        tmp_path = tmp_path.parent.parent / 'abc'

    tmp_path.mkdir(exist_ok=True, parents=True)
    tmp_path.joinpath('package.json').write_text('{"name": "another package.json"}')

    cache_dir = tmp_path / 'foo' / 'bar'
    cache_dir.mkdir(exist_ok=True, parents=True)

    monkeypatch.setenv('PYRIGHT_PYTHON_CACHE_DIR', str(cache_dir))

    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
    )
    assert proc.returncode == 0
