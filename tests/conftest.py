import pathlib

import pytest


def fixture_filenames():
    fixtures_dir = pathlib.Path(__file__).parent / 'fixtures'
    out_dir = fixtures_dir / 'out'
    in_dir = fixtures_dir / 'in'

    out_paths = list(out_dir.glob('*.py'))

    in_paths = [in_dir / out_path.name for out_path in out_paths]

    return list(zip(in_paths, out_paths))


def pytest_generate_tests(metafunc):
    argnames = ['in_file', 'out_file']
    if set(argnames).issubset(metafunc.fixturenames):
        metafunc.parametrize(argnames, fixture_filenames(), scope='session')
