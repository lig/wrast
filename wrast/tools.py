import ast
import os

from wrast import formatter


def wrasts(src: str) -> str:
    return formatter.Formatter().reformat(src)


def wrastf(src_path: os.PathLike) -> str:
    return wrasts(src_path.read_text())
