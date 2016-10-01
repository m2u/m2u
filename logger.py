"""
Setup and convenience functions for the logging module.
"""

import logging

from m2u import settings


def init_if_uninitialized():
    """ If there are no handlers yet, tell the logging module to do a
    default setup.
    """
    if len(logging.root.handlers) == 0:
        logging.basicConfig(format='# %(name)s : %(levelname)s : %(message)s')

        logger = logging.getLogger()
        level = logging.WARNING
        if settings.is_debug():
            level = logging.DEBUG
        logger.setLevel(level)
