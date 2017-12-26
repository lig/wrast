import ast

from wrast import formatter


def wrasts(src: str) -> str:
    return formatter.Formatter().reformat(src)
