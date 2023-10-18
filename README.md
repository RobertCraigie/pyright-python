# Pyright for Python

[![Downloads](https://pepy.tech/badge/pyright)](https://pepy.tech/project/pyright)
![PyPI](https://img.shields.io/pypi/v/pyright)
![Supported python versions](https://img.shields.io/pypi/pyversions/pyright)

> This project is not affiliated with Microsoft in any way, shape, or form

Pyright for Python is a Python command-line wrapper over [pyright](https://github.com/microsoft/pyright), a static type checker for Python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyright.

```bash
pip install pyright
```

## Usage

Pyright can be invoked using two different methods

```bash
pyright --help
```

or

```bash
python3 -m pyright --help
```

Pyright for Python should work exactly the same as pyright does, see the [pyright documentation](https://github.com/microsoft/pyright/blob/main/docs/getting-started.md) for details on how to make use of pyright.

### Pre-commit

You can also setup pyright to run automatically before each commit by setting up [pre-commit](https://pre-commit.com) and registering pyright in your `.pre-commit-config.yaml` file

```yaml
repos:
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.332
    hooks:
    - id: pyright
```

Pre-commit will install pyright-python in its own virtual environment which can cause pyright to not be able to detect your installed dependencies.

To fix this you can either [tell pre-commit](https://pre-commit.com/#config-additional_dependencies) to also install those dependencies or explicitly tell pyright which virtual environment to use by updating your [pyright configuration file](https://github.com/microsoft/pyright/blob/main/docs/configuration.md):

```toml
[tool.pyright]
# ...
venvPath = "."
venv = ".venv"
```

## Motivation

[Pyright](https://github.com/microsoft/pyright) is written in TypeScript, requiring node to be installed, and is normally installed with npm. This could be an entry barrier for some Python developers as they may not have node or npm installed on their machine; I wanted to make pyright as easy to install as any normal Python package.

## How Pyright for Python Works

This project works by first checking if node is in the `PATH`. If it is not, then we download node at runtime using [nodeenv](https://github.com/ekalinin/nodeenv), then install the pyright npm package using `npm` and finally, run the downloaded JS with `node`.

## Automatically keeping pyright up to date

By default Pyright for Python is set to target a specific pyright version and new releases will be automatically created whenever a new pyright version is released. It is highly recommended to use an automatic dependency update tool such as [dependabot](https://docs.github.com/en/code-security/supply-chain-security/managing-vulnerabilities-in-your-projects-dependencies/configuring-dependabot-security-updates).

If you would rather not have to update your installation every time a new pyright release is created then you can automatically use the latest available pyright version by setting the environment variable `PYRIGHT_PYTHON_FORCE_VERSION` to `latest`.

## Configuration

You can configure Pyright for Python using environment variables.

### Debugging

Set `PYRIGHT_PYTHON_DEBUG` to any value.

### Modify Pyright Version

Set `PYRIGHT_PYTHON_FORCE_VERSION` to the desired version, e.g. `1.1.156`, `latest`

### Show NPM logs

By default, Pyright for Python disables npm error messages, if you want to display the npm error messages then set `PYRIGHT_PYTHON_VERBOSE` to any truthy value.

### Modify NPM Package Location

Pyright for Python will resolve the root cache directory by checking the following environment variables, in order:

- `PYRIGHT_PYTHON_CACHE_DIR`
- `XDG_CACHE_HOME`

If neither of them are set it defaults to `~/.cache`

### Force Node Env

Set `PYRIGHT_PYTHON_GLOBAL_NODE` to any non-truthy value, i.e. anything apart from 1, t, on, or true.
e.g. `off`
You can optionally choose the version of node used by setting `PYRIGHT_PYTHON_NODE_VERSION` to the desired version

### Modify Node Env Location

Set `PYRIGHT_PYTHON_ENV_DIR` to a valid [nodeenv](https://github.com/ekalinin/nodeenv) directory. e.g. `~/.cache/nodeenv`

### Ignore Warnings

Set `PYRIGHT_PYTHON_IGNORE_WARNINGS` to a truthy value, e.g. 1, t, on, or true.

Pyright for Python will print warnings for the following case(s)

- There is a new Pyright version available.

## Contributing

All pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)
