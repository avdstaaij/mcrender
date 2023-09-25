"""Generic utilities."""

import sys
import os
import shutil


def eprint(*args, **kwargs):
    """Prints to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def move(src_path: str, dst_path: str, overwrite: bool = False, never_overwrite_dir: bool = False):
    """Moves a file or directory.

    There are three built-in functions for moving: os.rename, os.replace and shutil.move.
    The first two do not support moving between different file systems. The last one does, but it
    has possibly confusing semantincs when moving to a directory, and whether or not it overwrites
    an existing file or directory is not configurable and depends on the operating system.

    This function fixes these issues, at the cost of having TOCTOU vulnerabilities.

    If `overwrite==True`, overwrites any existing file at dst_path.
    If, in addition, `never_overwrite_dir==False`, also overwrites any existing directory.
    If `overwrite==False`, changing `never_overwrite_dir` will only affect exception messages.
    """

    if os.path.isfile(dst_path):
        if not overwrite:
            raise FileExistsError(f"File {dst_path} already exists.")
        try:
            shutil.move(src_path, dst_path)
        except FileExistsError:
            os.remove(dst_path)
            shutil.move(src_path, dst_path)
        return

    if os.path.isdir(dst_path):
        if never_overwrite_dir:
            raise FileExistsError(f"Not overwriting directory {dst_path}")
        if not overwrite:
            raise FileExistsError(f"Directory {dst_path} already exists.")
        shutil.rmtree(dst_path)
        shutil.move(src_path, dst_path)
        return

    shutil.move(src_path, dst_path)
