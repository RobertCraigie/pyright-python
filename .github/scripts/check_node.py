import sys
import shutil
import subprocess


def main(*args: str) -> None:
    print(args)
    node = shutil.which('node')
    assert node
    output = subprocess.check_output([node, '--version'])
    print(output)
    assert False


if __name__ == '__main__':
    main(*sys.argv[:1])
