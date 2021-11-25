import sys
import shutil
import subprocess


def main(*args: str) -> None:
    expected_version = f'v{args[0]}'
    node = shutil.which('node')
    assert node is not None
    output = subprocess.check_output([node, '--version']).decode('utf-8')
    if not output.startswith(expected_version):
        raise RuntimeError(
            f'Expected node version to start with: {expected_version} but got '
            + f'version: {output} instead.'
        )


if __name__ == '__main__':
    main(*sys.argv[1:])
