import argparse
from fileinput import FileInput
import re
import sys
from packaging import version
import semver


def get_pyright_version() -> str:
    with open('pyright/__init__.py') as f:
        match = re.search(
            r'^__pyright_version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
        )
        if not match:
            raise RuntimeError('version is not set')

        return match.group(1)


def compare(ver: str) -> bool:
    return version.parse(get_pyright_version()) < version.parse(ver)


def set_pyright_ver(ver: str):
    with FileInput('pyright/__init__.py', inplace=True) as f:  # type: ignore
        for line in f:  # type: ignore
            line = re.sub(
                r'^__pyright_version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                f"__pyright_version__ = '{ver}'",
                line.rstrip(),  # type: ignore
            )  # type: ignore
            print(line)


def bump_pyright_package_ver():
    with FileInput('pyright/__init__.py', inplace=True) as f:  # type: ignore
        for line in f:  # type: ignore
            line = line.rstrip()  # type: ignore
            current_version = re.search(
                r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', line  # type:ignore
            )
            if current_version:
                line = f"__version__ = '{semver.VersionInfo.parse(current_version.group(1)).bump_patch()}'"  # type:ignore
            print(line)  # type: ignore


if __name__ == "__main__":
    # create a parser object
    parser = argparse.ArgumentParser(description="Version management")

    # add argument
    parser.add_argument(
        "--get", "-g", action='store_true', help="Get current pyright version"
    )
    parser.add_argument(
        "--compare",
        "-c",
        type=str,
        nargs=1,
        help="Compare pyright version. Exits with status code 1 if version is newer than current",
    )
    parser.add_argument("--set", "-s", type=str, nargs=1, help="Set pyright version")

    # parse the arguments from standard input
    args = parser.parse_args()

    if args.get:
        print(get_pyright_version())
    elif args.compare != None:
        if compare(args.compare[0]):
            print('1')
        else:
            print('0')
    elif args.set != None:
        set_pyright_ver(args.set[0])
        bump_pyright_package_ver()
