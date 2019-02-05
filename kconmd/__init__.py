"""Init."""

__author__ = 'Jinzhe Zeng'

import logging

import coloredlogs
from pkg_resources import DistributionNotFound, get_distribution

from .kconmd import kconMD

__all__ = ['kconMD']

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = ''

coloredlogs.install(
    fmt=f'%(asctime)s - kconMD {__version__} - %(levelname)s: %(message)s',
    level=logging.INFO, milliseconds=True)
