#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess


def run(*args: str) -> None:
    print('\n[running] ' + ' '.join(args) + '\n')
    subprocess.check_call(list(args))


def main() -> None:
    run(sys.executable, 'setup.py', 'sdist')
    run(sys.executable, 'setup.py', 'sdist', 'bdist_wheel')
    run('twine', 'upload', 'dist/*')


if __name__ == '__main__':
    main()
