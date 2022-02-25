from typing import List, Tuple

import pytest

from pyright import cli


@pytest.mark.parametrize(
    'npx,pyright,args,expected',
    [
        [(1, 0), '2', [], ['npx', 'pyright@2']],
        [(1, 0), '2', ['foo', 'bar'], ['npx', 'pyright@2', 'foo', 'bar']],
        [(7, 0), '2', [], ['npx', '--silent', '--yes', 'pyright@2']],
        [
            (7, 0),
            '2',
            ['foo', 'bar'],
            ['npx', '--silent', '--yes', 'pyright@2', 'foo', 'bar'],
        ],
        [
            (7, 0),
            '2',
            ['foo', '--', 'bar'],
            ['npx', '--silent', '--yes', 'pyright@2', 'foo', '--', 'bar'],
        ],
    ],
)
def test_target_version(
    npx: Tuple[int, ...], pyright: str, args: List[str], expected: List[str]
) -> None:
    assert expected == cli.build_cmd(*args, pyright_version=pyright, npx_version=npx)
