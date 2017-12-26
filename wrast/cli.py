import difflib

from wrast import wrasts


src: str = r"""
for i  in range(10):
  print('Hello World!')
  j = 0
  while j<3:
    j += 1

    print('...')




print('''
----
''')
"""


def main() -> None:

    dst: str = wrasts(src)

    print('----')
    print(
        ''.join(
            difflib.ndiff(
                src.splitlines(keepends=True), dst.splitlines(keepends=True))))
    print('----')
    print(dst)
