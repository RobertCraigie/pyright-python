import os
import logging
import tempfile
from pathlib import Path
from configparser import ConfigParser

from pydantic import BaseSettings, BaseConfig, Field, Extra


log: logging.Logger = logging.getLogger(__name__)


def env_to_bool(key: str, *, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default

    return value.lower() in {'1', 't', 'on', 'true'}


class Config(BaseSettings):
    """TODO"""

    global_node: bool = Field(default=True)
    pyright_version: str = Field(default='1.1.150')
    env_dir: Path = Field(
        default=Path(tempfile.gettempdir()) / 'pyright-prisma' / 'env'
    )

    class Config(BaseConfig):
        extra: Extra = Extra.forbid
        env_prefix: str = 'PYRIGHT_PYTHON_'


def _load_config() -> Config:
    # TODO: check different config locations
    loader = ConfigParser()
    loader.read('pyright-python.ini')

    if 'pyright-python' not in loader.sections():
        log.debug('config file has no pyright-python section')
        return Config()

    data = loader['pyright-python']

    environ = os.environ
    for name, field in Config.__fields__.items():
        for env in field.field_info.extra.get('env_names', []):
            value = environ.get(env)
            if value is None:
                value = os.environ.get(env.upper())

            if value is not None:
                data[name] = value

    return Config.parse_obj(data)


# TODO: lazy
config = _load_config()
