import os

from .parser import parse

__version__ = '0.2.0'

__all__ = ["configdir"]


def configdir(directory=None):
    """
    Parse a ConfigDir

    Args:
        directory (str): Directory path to config contents. Defaults to `/configdir`.
            Can be overridden with environmental variable `CONFIGDIR`.

    Returns:
        dict: Config values
    """
    directory = directory or os.getenv("CONFIGDIR", "/configdir")
    return parse(directory)
