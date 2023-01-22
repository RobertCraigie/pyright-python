from __future__ import annotations

import re


def assert_matches(pattern: re.Pattern[str], contents: str) -> re.Match[str]:
    match = pattern.search(contents)
    if match is None:
        raise ValueError(f'Pattern, {pattern}, did not match input: {contents}')

    return match
