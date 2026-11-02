import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_subprocess import FakeProcess
from pytest_subprocess.fake_popen import FakePopen

import pyright.node
from pyright.types import Target


@pytest.fixture
def nodeenv_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    env_dir = tmp_path / 'nodeenv'
    bin_dir = env_dir / 'bin'
    bin_dir.mkdir(parents=True)
    monkeypatch.setattr(pyright.node, 'ENV_DIR', env_dir)
    monkeypatch.setattr(pyright.node, 'BINARIES_DIR', bin_dir)
    monkeypatch.setattr(pyright.node, 'NODE_VERSION', '23.1.0')
    monkeypatch.setattr(pyright.node, 'USE_GLOBAL_NODE', False)
    monkeypatch.setattr(pyright.node, 'USE_NODEJS_WHEEL', False)
    for target in ('node', 'npm'):
        pyright.node._get_nodeenv_path(target).touch()
    return env_dir


@pytest.mark.parametrize('target', ['node', 'npm'])
@pytest.mark.parametrize('requested', ['23.1.0', 'v23.1.0'])
@pytest.mark.parametrize('output', [b'v23.1.0\n', b'23.1.0\n'])
def test_pinned_nodeenv_is_reused(
    target: Target,
    requested: str,
    output: bytes,
    nodeenv_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_process: FakeProcess,
) -> None:
    monkeypatch.setattr(pyright.node, 'NODE_VERSION', requested)
    node = str(pyright.node._get_nodeenv_path('node'))
    npm = str(pyright.node._get_nodeenv_path('npm'))
    install = [sys.executable, '-m', 'nodeenv', '--node', requested, '--force', str(nodeenv_dir)]
    fake_process.register([node, '--version'], stdout=output, occurrences=4)  # pyright: ignore[reportUnknownMemberType]
    fake_process.register([npm, '--version'], stdout=b'10.8.0\n', occurrences=2)  # pyright: ignore[reportUnknownMemberType]
    fake_process.register(install, occurrences=2)  # pyright: ignore[reportUnknownMemberType]

    for _ in range(2):
        result = pyright.node.run(target, '--version', stdout=subprocess.PIPE, check=True)
        assert result.stdout == (output if target == 'node' else b'10.8.0\n')

    assert fake_process.call_count(install) == 0  # pyright: ignore[reportUnknownMemberType]


def test_changed_node_version_is_installed_once(
    nodeenv_dir: Path, monkeypatch: pytest.MonkeyPatch, fake_process: FakeProcess
) -> None:
    node = str(pyright.node._get_nodeenv_path('node'))
    fake_process.register([node, '--version'], stdout=b'v23.1.0\n', occurrences=3)  # pyright: ignore[reportUnknownMemberType]
    fake_process.register([node, '--version'], stdout=b'v24.0.0\n', occurrences=3)  # pyright: ignore[reportUnknownMemberType]
    install = [sys.executable, '-m', 'nodeenv', '--node', '24.0.0', '--force', str(nodeenv_dir)]
    fake_process.register(install)  # pyright: ignore[reportUnknownMemberType]

    first = pyright.node.run('node', '--version', stdout=subprocess.PIPE, check=True)
    monkeypatch.setattr(pyright.node, 'NODE_VERSION', '24.0.0')
    second = pyright.node.run('node', '--version', stdout=subprocess.PIPE, check=True)
    third = pyright.node.run('node', '--version', stdout=subprocess.PIPE, check=True)

    assert first.stdout == b'v23.1.0\n'
    assert second.stdout == third.stdout == b'v24.0.0\n'
    assert fake_process.call_count(install) == 1  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize(
    'requested,output,returncode',
    [
        ('latest', b'v23.1.0\n', 0),
        ('lts', b'v23.1.0\n', 0),
        ('23', b'v23.1.0\n', 0),
        ('23.1', b'v23.1.0\n', 0),
        ('23.1.0rc1', b'v23.1.0\n', 0),
        ('23.1.0', b'v22.1.0\n', 0),
        ('23.1.0', b'', 0),
        ('23.1.0', b'Node v23.1.0\n', 0),
        ('23.1.0', b'vv23.1.0\n', 0),
        ('23.1.0', b'v23.1.0-extra\n', 0),
        ('23.1.0', b'\xff', 0),
        ('23.1.0', b'v23.1.0\n', 1),
    ],
)
def test_uncertain_node_version_is_reinstalled(
    requested: str,
    output: bytes,
    returncode: int,
    nodeenv_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_process: FakeProcess,
) -> None:
    monkeypatch.setattr(pyright.node, 'NODE_VERSION', requested)
    node = str(pyright.node._get_nodeenv_path('node'))
    fake_process.register([node, '--version'], stdout=output, returncode=returncode)  # pyright: ignore[reportUnknownMemberType]
    install = [sys.executable, '-m', 'nodeenv', '--node', requested, '--force', str(nodeenv_dir)]
    fake_process.register(install)  # pyright: ignore[reportUnknownMemberType]

    assert pyright.node._ensure_node_env('node') == Path(node)
    assert fake_process.call_count(install) == 1  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.usefixtures('nodeenv_dir')
def test_node_probe_has_a_bounded_timeout(fake_process: FakeProcess) -> None:
    node = str(pyright.node._get_nodeenv_path('node'))
    fake_process.register([node, '--version'], stdout=b'v23.1.0\n')  # pyright: ignore[reportUnknownMemberType]

    with patch.object(pyright.node.subprocess, 'run', wraps=subprocess.run) as probe:
        assert pyright.node._ensure_node_env('node') == Path(node)

    assert 0 < probe.call_args[1]['timeout'] <= 5


@pytest.mark.parametrize('error', [OSError('not executable'), subprocess.TimeoutExpired('node', 5)])
def test_failed_node_probe_reinstalls(error: Exception, nodeenv_dir: Path, fake_process: FakeProcess) -> None:
    node = str(pyright.node._get_nodeenv_path('node'))

    def fail_probe(_process: FakePopen) -> None:
        raise error

    fake_process.register([node, '--version'], callback=fail_probe)  # pyright: ignore[reportUnknownMemberType]
    install = [sys.executable, '-m', 'nodeenv', '--node', '23.1.0', '--force', str(nodeenv_dir)]
    fake_process.register(install)  # pyright: ignore[reportUnknownMemberType]

    assert pyright.node._ensure_node_env('node') == Path(node)
    assert fake_process.call_count(install) == 1  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.parametrize('target,missing', [('node', 'node'), ('npm', 'npm'), ('npm', 'node')])
def test_missing_nodeenv_binary_is_installed(
    target: Target, missing: Target, nodeenv_dir: Path, fake_process: FakeProcess
) -> None:
    pyright.node._get_nodeenv_path(missing).unlink()
    node = str(pyright.node._get_nodeenv_path('node'))

    def probe(_process: FakePopen) -> None:
        if missing == 'node':
            raise FileNotFoundError(node)

    def install_binaries(_process: FakePopen) -> None:
        for name in ('node', 'npm'):
            pyright.node._get_nodeenv_path(name).touch()

    fake_process.register([node, '--version'], stdout=b'v23.1.0\n', callback=probe)  # pyright: ignore[reportUnknownMemberType]
    install = [sys.executable, '-m', 'nodeenv', '--node', '23.1.0', '--force', str(nodeenv_dir)]
    fake_process.register(install, callback=install_binaries)  # pyright: ignore[reportUnknownMemberType]

    assert pyright.node._ensure_node_env(target) == pyright.node._get_nodeenv_path(target)
    assert fake_process.call_count(install) == 1  # pyright: ignore[reportUnknownMemberType]


def test_unpinned_nodeenv_is_reused_without_probe(
    nodeenv_dir: Path, monkeypatch: pytest.MonkeyPatch, fake_process: FakeProcess
) -> None:
    monkeypatch.setattr(pyright.node, 'NODE_VERSION', None)
    install = [sys.executable, '-m', 'nodeenv', str(nodeenv_dir)]
    fake_process.register(install)  # pyright: ignore[reportUnknownMemberType]

    pyright.node._ensure_node_env('node')
    pyright.node._ensure_node_env('npm')

    assert not fake_process.calls  # pyright: ignore[reportUnknownMemberType]
