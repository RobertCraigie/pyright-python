#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()

version = ''
with open('pyright/_version.py') as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError('version is not set')

    version = match.group(1)

if not version:
    raise RuntimeError('version is not set')


with open('requirements.txt', 'r') as f:
    requirements = f.readlines()


extras = {
    'dev': [
        'twine>=3.4.1',
    ]
}

setup(
    name='pyright',
    version=version,
    author='Robert Craigie',
    maintainer='Robert Craigie',
    license='MIT',
    url='https://github.com/RobertCraigie/pyright-python',
    description='Command line wrapper for pyright',
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['pyright'],
    python_requires='>=3.7',
    package_data={'': ['py.typed']},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pyright=pyright.cli:entrypoint',
            'pyright-python=pyright.cli:entrypoint',
            'pyright-langserver=pyright.langserver:entrypoint',
            'pyright-python-langserver=pyright.langserver:entrypoint',
        ],
    },
    extras_require={
        **extras,
        'all': [req for requirements in extras.values() for req in requirements],
    },
    project_urls={
        'Source': 'https://github.com/RobertCraigie/pyright-python',
        'Tracker': 'https://github.com/RobertCraigie/pyright-python/issues',
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Typing :: Typed',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
