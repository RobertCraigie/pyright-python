import re
import sys
import subprocess


VERSION_REGEX = re.compile(r'pyright (?P<version>\d+\.\d+\.\d+)')


def test_module_invocation() -> None:
    proc = subprocess.run(
        [sys.executable, '-m', 'pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    match = VERSION_REGEX.match(output)
    assert match is not None


def test_entry_point() -> None:
    proc = subprocess.run(
        ['pyright', '--version'],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert proc.returncode == 0
    output = proc.stdout.decode('utf-8')
    match = VERSION_REGEX.match(output)
    assert match is not None
