from __future__ import annotations

import re
from os import PathLike
from pathlib import Path
from typing_extensions import TypeAlias

StrPath: TypeAlias = 'str | PathLike[str]'


def assert_matches(pattern: re.Pattern[str], contents: str) -> re.Match[str]:
    match = pattern.search(contents)
    if match is None:
        raise ValueError(f'Pattern, {pattern}, did not match input: {contents}')

    return match


def is_relative_to(path: StrPath, to: StrPath) -> bool:
    """Backport of Path.is_relative_to for Python < 3.9"""
    try:
        Path(path).relative_to(to)
        return True
    except ValueError:
        return False
