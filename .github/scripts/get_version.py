import re
from pathlib import Path


def main() -> None:
    path = Path(__file__).parent.parent.parent / 'pyright' / '_version.py'
    contents = path.read_text()
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', contents, re.MULTILINE)
    if match is None:
        raise RuntimeError('Could not find version')

    print(match.group(1), end='')


if __name__ == '__main__':
    main()
