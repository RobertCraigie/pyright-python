import os
import sys
import pipes
import shutil
import logging
import subprocess
from typing import Dict, Optional, Any
from pathlib import Path

from .types import Binary, Target, Strategy, check_target
from .utils import config


log: logging.Logger = logging.getLogger(__name__)


def _ensure_available(target: Target) -> Binary:
    """Ensure the target node executable is available"""
    path = None
    if config.global_node:
        path = _get_global_binary(target)

    if path is not None:
        return Binary(path=path, strategy=Strategy.GLOBAL)

    return Binary(path=_ensure_node_env(target), strategy=Strategy.NODEENV)


def _ensure_node_env(target: Target) -> Path:
    log.debug('Checking for nodeenv %s binary', target)

    env_dir = config.env_dir
    if not env_dir.exists():
        log.debug('Environment not found at %s', env_dir)
        _install_node_env()
    else:
        log.debug('Environment exists at %s', env_dir)

    # Ensure the target binary exists.
    # This shouldn't really happen but there could
    # be cases where our env dir exists but without the
    # binary so we might as well just double check.
    path = env_dir.joinpath('bin').joinpath(target)
    if not path.exists():
        _install_node_env()

    if not path.exists():
        raise RuntimeError(
            f'Expected {target} binary to exist at {path} but was not found.'
        )
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
    log.debug('Installing nodeenv to %s', config.env_dir)
    args = [sys.executable, '-m', 'nodeenv', str(config.env_dir)]
    log.debug('Running command with args: %s', args)
    subprocess.run(args, check=True)


def run(target: Target, *args: str) -> int:
    check_target(target)
    binary = _ensure_available(target)
    env = os.environ.copy()

    if binary.strategy == Strategy.NODEENV:
        activate = binary.path.parent / 'activate'
        node_args = [
            'bash',
            '-c',
            f'. {pipes.quote(str(activate))} && {" ".join([target, *args])}',
        ]
        env.update(get_env_variables())
    elif binary.strategy == Strategy.GLOBAL:
        node_args = [str(binary.path), *args]
    else:
        raise RuntimeError(f'Unknown strategy: {binary.strategy}')

    log.debug('Running node command with args: %s', node_args)

    proc = subprocess.run(node_args, env=env)
    return proc.returncode


def get_env_variables() -> Dict[str, Any]:
    """Return the environmental variables that should be passed to a binary"""
    # NOTE: I do not actually know if these result in the intended behaviour
    #       I simply copied them from bin/shim in nodeenv
    return {
        'NODE_PATH': str(config.env_dir / 'lib' / 'node_modules'),
        'NPM_CONFIG_PREFIX': str(config.env_dir),
        'npm_config_prefix': str(config.env_dir),
    }
