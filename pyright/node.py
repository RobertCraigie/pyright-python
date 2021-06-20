import os
import sys
import pipes
import logging
import subprocess
from typing import Dict, Any
from pathlib import Path

from .utils import get_env_dir


log: logging.Logger = logging.getLogger(__name__)

ENV_DIR: Path = get_env_dir()
BINARIES_DIR: Path = ENV_DIR / 'bin'


def ensure_available() -> Path:
    """Ensure the node executable is available

    Returns the path of the bin/ directory containing node
    """
    if not ENV_DIR.exists():
        _install_node_env()
    else:
        log.debug('Environment exists at %s', ENV_DIR)

    # Ensure all the binaries we require are installed.
    # This shouldn't really happen but there could
    # be cases where our env dir exists but without the
    # binaries so we might as well just double check.
    for binary in ['node', 'npm', 'npx']:
        if not BINARIES_DIR.joinpath(binary).exists():
            _install_node_env()

    path = BINARIES_DIR.joinpath('node')
    if not path.exists():
        raise RuntimeError(f'Expected node to exist at {path}')
    return BINARIES_DIR


def _install_node_env() -> None:
    args = [sys.executable, '-m', 'nodeenv', str(ENV_DIR)]
    log.debug('Running command with args: %s', args)
    subprocess.run(args, check=True)


def run(*args: str) -> int:
    ensure_available()

    activate = ENV_DIR / 'bin' / 'activate'
    new_args = ('bash', '-c', f'. {pipes.quote(str(activate))} && {" ".join(args)}')
    log.debug('Running node command with args: %s', new_args)

    proc = subprocess.run(new_args, env={**os.environ, **get_env_variables()})
    return proc.returncode


def get_env_variables() -> Dict[str, Any]:
    """Return the environmental variables that should be passed to a binary"""
    # NOTE: I do not actually know if these result in the intended behaviour
    #       I simply copied them from bin/shim in nodeenv
    return {
        'NODE_PATH': str(ENV_DIR / 'lib' / 'node_modules'),
        'NPM_CONFIG_PREFIX': str(ENV_DIR),
        'npm_config_prefix': str(ENV_DIR),
    }
