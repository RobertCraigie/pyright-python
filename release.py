#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from pyright import __version__


def run(*args: str) -> None:
    print('\n[running] ' + ' '.join(args) + '\n')
    subprocess.check_call(list(args))


def main() -> None:
    run('git', 'tag', '-s', f'v{__version__}', '-m', f'{__version__} release')
    run('git', 'push', '--tags')

    run(sys.executable, 'setup.py', 'sdist')
    run(sys.executable, 'setup.py', 'sdist', 'bdist_wheel')
    run('twine', 'upload', 'dist/*')


if __name__ == '__main__':
    main()
