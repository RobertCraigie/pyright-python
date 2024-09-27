from __future__ import annotations

import pytest

from pyright._utils import _should_warn_version


@pytest.fixture(autouse=True)
def mock_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('PYRIGHT_PYTHON_IGNORE_WARNINGS', raising=False)
    monkeypatch.delenv('PYRIGHT_PYTHON_PYLANCE_VERSION', raising=False)

    def _get_latest_version() -> None:
        raise RuntimeError('this should be overriden in tests')

    monkeypatch.setattr('pyright._utils.get_latest_version', _get_latest_version)


def test_quiet_flag() -> None:
    assert not _should_warn_version(args=(), quiet=True)


def test_outputjson_flag() -> None:
    assert not _should_warn_version(args=('--outputjson',), quiet=None)


@pytest.mark.parametrize(
    'env_value, expected',
    [
        ('1', False),
        ('true', False),
        ('0', True),
        ('false', True),
    ],
)
def test_ignore_warnings_env_var(monkeypatch: pytest.MonkeyPatch, env_value: str, expected: bool) -> None:
    monkeypatch.setenv('PYRIGHT_PYTHON_IGNORE_WARNINGS', env_value)

    if expected is True:
        monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.1')
        monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    else:
        monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.0')
        monkeypatch.setattr('pyright._utils.__version__', '1.0.0')

    assert _should_warn_version(args=(), quiet=None) == expected


def test_pylance_version_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.1')
    monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    monkeypatch.setenv('PYRIGHT_PYTHON_PYLANCE_VERSION', '1.0.0')
    assert not _should_warn_version(args=(), quiet=None)


def test_force_version_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.1')
    monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    monkeypatch.setenv('PYRIGHT_PYTHON_FORCE_VERSION', '0.9.9')
    assert _should_warn_version(args=(), quiet=None)


def test_version_comparison(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.1')
    monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    assert _should_warn_version(args=(), quiet=None)

    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.0')
    monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    assert not _should_warn_version(args=(), quiet=None)

    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: None)
    assert not _should_warn_version(args=(), quiet=None)


def test_default_behavior(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('pyright._utils.get_latest_version', lambda: '1.0.1')
    monkeypatch.setattr('pyright._utils.__version__', '1.0.0')
    assert _should_warn_version(args=(), quiet=None)
