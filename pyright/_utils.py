from getpass import getuser
import hashlib


def get_tmp_path_suffix() -> str:
    try:
        user = getuser()
    except Exception:
        return ''

    return f'.{hashlib.md5(user.encode()).hexdigest()}'
