#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import shutil
import subprocess
from pathlib import Path
from pyright import __version__


def run(*args: str) -> None:
    print('\n[running] ' + ' '.join(args) + '\n')
    subprocess.check_call(list(args))


def main() -> None:
    dist = Path(__file__).parent / 'dist'
    if dist.exists():
        shutil.rmtree(str(dist))

    run('git', 'tag', '-s', f'v{__version__}', '-m', f'{__version__} release')
    run('git', 'push', '--tags')

    run(sys.executable, 'setup.py', 'sdist')
    run(sys.executable, 'setup.py', 'sdist', 'bdist_wheel')
    run('twine', 'upload', 'dist/*')


if __name__ == '__main__':
    main()
