# -*- coding: utf-8 -*-
# pyright: reportUnusedImport=false

__title__ = 'pyright'
__author__ = 'RobertCraigie'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021 Robert Craigie'
__version__ = '0.0.9'


import os
from . import errors
from .cli import *


if os.environ.get('PYRIGHT_PYTHON_DEBUG'):
    import logging

    logging.basicConfig(
        format='%(asctime)-15s - %(levelname)s - %(name)s - %(message)s'
    )
    logging.getLogger('pyright').setLevel(logging.DEBUG)
