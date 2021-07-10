# Pyright for Python

> This project is not affiliated with Microsoft in any way, shape or form

Pyright for Python is a Python command line wrapper over [pyright](https://github.com/microsoft/pyright), a static type checker for Python.

**This project is not suitable for production usage.**

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

## Motivation

[Pyright](https://github.com/microsoft/pyright) is written in TypeScript and requires node to be installed and is normally installed with npm, this could be a barrier for entry for some python developers as they may not have node or npm, installed on their machine, I wanted to make pyright as easy to install as any normal python package.


## How Pyright for Python Works

This project works by first checking if node is in the `PATH` and if it is not then we download node at runtime using [nodeenv](https://github.com/ekalinin/nodeenv) and then install the pyright npm package using `npx`.

## Configuration

You can configure Pyright for Python using environment variables.

### Debugging

Set `PYRIGHT_PYTHON_DEBUG` to any value.

### Modify Pyright Version

Set `PYRIGHT_PYTHON_VERSION` to the desired version, e.g. `1.1.150`

## Force Node Env

Set `PYRIGHT_PYTHON_GLOBAL_NODE` to any non-truthy value, i.e. anything apart from 1, t, on or true.
e.g. `off`

### Modify Node Env Location

Set `PYRIGHT_PYTHON_ENV_DIR` to a valid  [nodeenv](https://github.com/ekalinin/nodeenv) directory. e.g. `~/.cache/nodeenv`

## Contributing

All pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)
