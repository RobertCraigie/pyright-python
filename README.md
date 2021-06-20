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


## Implementation Notes

This project works by downloading node at runtime using [nodeenv](https://github.com/ekalinin/nodeenv) and then installing pyright, while this works, it is far from ideal.

There are at least two options for fixing this problem, the first is to package a wheel for each platform containing a node binary, I do not know if we can get around installing pyright at runtime as `npm install` could have platform specific dependencies.

The second option is to use [pkg](https://github.com/vercel/pkg) to create a pyright binary and package that in wheels.

## Configuration

You can configure Pyright for Python using environment variables.

### Debugging

Set `PYRIGHT_PYTHON_DEBUG` to any value.

### Modify Pyright Version

Set `PYRIGHT_PYTHON_VERSION` to the desired version, e.g. `1.1.150`

### Modify Node Env Location

Set `PYRIGHT_PYTHON_ENV_DIR` to a valid  [nodeenv](https://github.com/ekalinin/nodeenv) directory. e.g. `~/.cache/nodeenv`

## Contributing

All pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)
