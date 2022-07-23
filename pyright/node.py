import os
import re
import sys
import pipes
import shutil
import logging
import subprocess
from functools import lru_cache
from typing import Dict, Tuple, Optional, Union, Any
from pathlib import Path

from . import errors
from .types import Binary, Target, Strategy, check_target
from .utils import get_env_dir, env_to_bool, maybe_decode


log: logging.Logger = logging.getLogger(__name__)

ENV_DIR: Path = get_env_dir()
BINARIES_DIR: Path = ENV_DIR / 'bin'
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


def _ensure_node_env(target: Target) -> Path:
    log.debug('Checking for nodeenv %s binary', target)

    if not ENV_DIR.exists():
        log.debug('Environment not found at %s', ENV_DIR)
        _install_node_env()
    else:
        log.debug('Environment exists at %s', ENV_DIR)

    # Ensure the target binary exists.
    # This shouldn't really happen but there could
    # be cases where our env dir exists but without the
    # binary so we might as well just double check.
    path = BINARIES_DIR.joinpath(target)
    if not path.exists():
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
    env = os.environ.copy()

    if binary.strategy == Strategy.NODEENV:
        env.update(get_env_variables())

        if shutil.which('bash'):
            activate = binary.path.parent / 'activate'
            node_args = [
                'bash',
                '-c',
                f'. {pipes.quote(str(activate))} && {" ".join([target, *args])}',
            ]
        else:
            if not env_to_bool('PYRIGHT_PYTHON_IGNORE_WARNINGS', default=False):
                print(
                    'WARNING: nodeenv usage without access to bash, this is untested behaviour.\n'
                )

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
