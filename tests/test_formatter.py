import pytest

from wrast import wrasts


def test_code(in_file, out_file):
    assert wrasts(in_file.read_text()) == out_file.read_text()
