import pathlib

import click

from wrast import wrastf
import logging


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def main(filename) -> None:
    logging.basicConfig(level=logging.DEBUG)
    print(wrastf(pathlib.Path(filename)))
