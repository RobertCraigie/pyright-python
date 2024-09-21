import pytest

from pyright.types import check_target


def test_check_target() -> None:
    with pytest.raises(TypeError) as exc:
        check_target('foo')

    assert exc.match(r'foo is not a valid target, expected one of ((npm|node), )+')
    check_target('npm')
    check_target('node')
