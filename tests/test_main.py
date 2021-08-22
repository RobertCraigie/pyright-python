import re
import sys
import json
import subprocess
from pathlib import Path

import pyright


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


def test_long_arguments(tmp_path: Path) -> None:
    """Long arguments (e.g. --outputjson) are passed to the pyright CLI"""
    tmp_path.joinpath('foo.py').write_text('reveal_type(1)')

    result = pyright.run('--outputjson', 'foo.py', stdout=subprocess.PIPE)
    assert result.returncode == 0

    data = json.loads(result.stdout)
    assert data['generalDiagnostics'][0]['message'] == 'Type of "1" is "Literal[1]"'
