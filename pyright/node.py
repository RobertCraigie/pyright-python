from __future__ import annotations

import os
import re
import sys
import json
import shutil
import logging
import platform
import subprocess
from functools import lru_cache
from typing import Dict, Mapping, Tuple, Optional, Union, Any
from pathlib import Path

from . import errors
from .types import Binary, Target, Strategy, check_target
from .utils import get_env_dir, env_to_bool, get_bin_dir, maybe_decode


log: logging.Logger = logging.getLogger(__name__)

ENV_DIR: Path = get_env_dir()
BINARIES_DIR: Path = get_bin_dir(env_dir=ENV_DIR)
USE_GLOBAL_NODE = env_to_bool('PYRIGHT_PYTHON_GLOBAL_NODE', default=True)
VERSION_RE = re.compile(r'\d+\.\d+\.\d+')


def _ensure_available(target: Target) -> Binary:
    """Ensure the target node executable is available"""
    path = None
    if USE_GLOBAL_NODE:
        path = _get_global_binary(target)

    if path is not None:
        return Binary(path=path, strategy=Strategy.GLOBAL)

    return Binary(path=_ensure_node_env(target), strategy=Strategy.NODEENV)


def _is_windows() -> bool:
    return platform.system().lower() == 'windows'


def _postfix_for_target(target: Target) -> str:
    if not _is_windows():
        return ''

    if target == 'node':
        return '.exe'
    return '.cmd'


def _ensure_node_env(target: Target) -> Path:
    log.debug('Checking for nodeenv %s binary', target)

    path = BINARIES_DIR.joinpath(target + _postfix_for_target(target))

    log.debug('Using %s path for binary', path)

    if path.exists():
        log.debug('Binary at %s exists, skipping nodeenv installation', path)
    else:
        log.debug('Installing nodeenv as a binary at %s could not be found', path)
        _install_node_env()

    if not path.exists():
        raise errors.BinaryNotFound(path=path, target=target)
    return path


def _get_global_binary(target: Target) -> Optional[Path]:
    log.debug('Checking for global target binary: %s', target)

    which = shutil.which(target)
    if which is not None:
        log.debug('Found global binary at: %s', which)

        path = Path(which)
        if path.exists():
            log.debug('Global binary exists at: %s', which)
            return path

    log.debug('Global target binary: %s not found', target)
    return None


def _install_node_env() -> None:
    log.debug('Installing nodeenv to %s', ENV_DIR)
    args = [sys.executable, '-m', 'nodeenv', str(ENV_DIR)]
    log.debug('Running command with args: %s', args)
    subprocess.run(args, check=True)


def _run_gracefully(
    *popen_args: Any,
    input: Optional[str] = None,
    capture_output: bool = False,
    timeout: Optional[float] = None,
    check: bool = False,
    **kwargs: Any,
) -> Union['subprocess.CompletedProcess[bytes]', 'subprocess.CompletedProcess[str]']:
    """Similar to subprocess.run, but mindful of potential errors."""

    # Because subprocess doesn't provide any better interface, to keep things compatible
    # this re-implements almost everything in subprocess.run
    if input is not None:
        if kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError(
                'stdout and stderr arguments may not be used with capture_output.'
            )
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    log.debug(f"Gracefully running command {popen_args}")
    process = subprocess.Popen(*popen_args, **kwargs)
    try:
        stdout, stderr = process.communicate(input, timeout=timeout)
        return_code = process.wait()
    except Exception as exc:
        log.debug("Caught exception while running command, handling gracefully.")
        try:
            print("\nTerminating process, please wait for cleanup to finish...")
            process.terminate()
            return_code = process.wait()
            stdout, stderr = process.communicate()
            print("Process terminated")
        except Exception as exc2:
            log.debug(
                "Caught another exception during graceful termination, force-killing process."
            )
            process.kill()
            process.wait()
            print("\nKilling child process without cleanup. This may lead to issues.")
            raise exc2 from exc

    log.debug(f"Process finished with exit code {return_code}.")
    result = subprocess.CompletedProcess(process.args, return_code, stdout, stderr)
    if check:
        result.check_returncode()
    return result


def run(
    target: Target, *args: str, **kwargs: Any
) -> Union['subprocess.CompletedProcess[bytes]', 'subprocess.CompletedProcess[str]']:
    check_target(target)
    binary = _ensure_available(target)
    env = kwargs.pop('env', None) or os.environ.copy()

    if binary.strategy == Strategy.NODEENV:
        env.update(get_env_variables())

        # If we're using `nodeenv` to resolve the node binary then we also need
        # to ensure that `node` is in the PATH so that any install scripts that
        # assume it is present will work.
        env.update(PATH=_update_path_env(env=env, target_bin=binary.path.parent))
        node_args = [str(binary.path), *args]
    elif binary.strategy == Strategy.GLOBAL:
        node_args = [str(binary.path), *args]
    else:
        raise RuntimeError(f'Unknown strategy: {binary.strategy}')

    log.debug('Running node command with args: %s', node_args)
    return _run_gracefully(node_args, env=env, **kwargs)


def version(target: Target) -> Tuple[int, ...]:
    proc = run(target, '--version', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = maybe_decode(proc.stdout)
    match = VERSION_RE.search(output)
    if not match:
        print(output, file=sys.stderr)
        raise errors.VersionCheckFailed(
            f'Could not find version from `{target} --version`, see output above'
        )

    info = tuple(int(value) for value in match.group(0).split('.'))
    log.debug('Version check for %s returning %s', target, info)
    return info


@lru_cache(maxsize=None)
def latest(package: str) -> str:
    """Return the latest version for the given package"""
    proc = run(
        'npm',
        'info',
        package,
        'version',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout = maybe_decode(proc.stdout)

    if proc.returncode != 0:
        print(stdout, file=sys.stderr)
        raise errors.VersionCheckFailed(
            f'Version check for {package} failed, see output above.'
        )

    match = VERSION_RE.search(stdout)
    if not match:
        print(stdout, file=sys.stderr)
        raise errors.VersionCheckFailed(
            f'Could not find version for {package}, see output above'
        )

    value = match.group(0)
    log.debug('Version check for %s returning %s', package, value)
    return value


def get_env_variables() -> Dict[str, Any]:
    """Return the environmental variables that should be passed to a binary"""
    # NOTE: I do not actually know if these result in the intended behaviour
    #       I simply copied them from bin/shim in nodeenv
    return {
        'NODE_PATH': str(ENV_DIR / 'lib' / 'node_modules'),
        'NPM_CONFIG_PREFIX': str(ENV_DIR),
        'npm_config_prefix': str(ENV_DIR),
    }


def get_pkg_version(pkg: Path) -> str | None:
    """Given a path to a `package.json` file, parse it and returns the `version` property

    Returns `None` if the version could not be resolved for any reason.
    """
    if not pkg.exists():
        return None

    try:
        data = json.loads(pkg.read_text())
    except Exception:
        # TODO: test this
        log.debug(
            'Ignoring error while reading/parsing the %s file', pkg, exc_info=True
        )
        return None

    return data.get('version')


def _update_path_env(
    *,
    env: Mapping[str, str] | None,
    target_bin: Path,
    sep: str = os.pathsep,
) -> str:
    """Returns a modified version of the `PATH` environment variable that has been updated
    to include the location of the downloaded Node binaries.
    """
    if env is None:
        env = dict(os.environ)

    log.debug('Attempting to prepend %s to the PATH', target_bin)
    assert target_bin.exists(), f'Target directory {target_bin} does not exist'

    path = env.get('PATH', '') or os.environ.get('PATH', '')
    if path:
        log.debug('Found PATH contents: %s', path)

        # handle the case where the PATH already starts with the separator (this probably shouldn't happen)
        if path.startswith(sep):
            path = f'{target_bin.absolute()}{path}'
        else:
            path = f'{target_bin.absolute()}{sep}{path}'
    else:
        # handle the case where there is no PATH set (unlikely / impossible to actually happen?)
        path = str(target_bin.absolute())

    log.debug('Using PATH environment variable: %s', path)
    return path
