import json
import os
import time
import subprocess


# TODO: more tests


def test_entry_point() -> None:
    proc = subprocess.run(
        ['pyright-langserver'],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert proc.returncode == 1
    output = proc.stdout.decode('utf-8')
    assert 'Connection input stream is not set' in output


def test_user_special_characters() -> None:
    proc = subprocess.run(
        ['pyright-langserver'],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={
            **os.environ,
            'LOGNAME': 'alice@example.com',
        },
    )
    assert proc.returncode == 1
    output = proc.stdout.decode('utf-8')
    assert 'Connection input stream is not set' in output


def test_only_json_output() -> None:
    """The language server should only output valid JSON"""
    proc = subprocess.Popen(
        ['pyright-langserver', '--stdio'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)
    proc.kill()
    assert proc.stdout is not None

    stdout = proc.stdout.read().decode('utf-8')
    for line in stdout.splitlines():
        json.loads(line)
