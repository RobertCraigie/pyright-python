import io
import sys
import json
import shutil
import tarfile
from pathlib import Path

import pyright
from pyright import _mureq, __pyright_version__

DIST_DIR = Path(pyright.__file__).parent / 'dist'


def _should_download() -> bool:
    if '--force' in sys.argv:
        return True

    pkg_path = DIST_DIR / 'package.json'
    if not pkg_path.exists():
        return True

    pkg_json = json.loads(pkg_path.read_text())
    if pkg_json['version'] == __pyright_version__:
        print(
            f'skipping download as the current pyright version ({__pyright_version__}) is already downloaded. use --force to override'
        )
        return False

    return True


def download_tarball(*, version: str) -> None:
    if not _should_download():
        return

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    rsp = _mureq.get(f'https://registry.npmjs.org/pyright/{version}')
    rsp.raise_for_status()

    info = rsp.json()
    tar_url = info['dist']['tarball']
    print(f'downloading tar from {tar_url}')

    rsp = _mureq.get(tar_url)
    rsp.raise_for_status()

    with tarfile.open(fileobj=io.BytesIO(rsp.body)) as tar:
        members = tar.getmembers()

        # npm tarballs will always output one `package/` directory which is
        # not necessary for our case, so we strip out the `package/` prefix
        for member in members:
            if member.path.startswith('package/'):
                member.path = member.path.replace('package/', '', 1)
            else:
                raise RuntimeError(f'expected tar member path to start with `package/` but got {member.path}')

        tar.extractall(path=DIST_DIR, members=members)


def main() -> None:
    download_tarball(version=__pyright_version__)


if __name__ == '__main__':
    main()
