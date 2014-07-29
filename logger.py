"""
setup and convenience functions for the logging module
"""

import m2u.settings as settings
import logging


def initIfUninitialized():
    """ if there are no handlers yet, tell the logging module
    to do a default setup
    """
    if len(logging.root.handlers)==0:
        logging.basicConfig(format='# %(name)s : %(levelname)s : %(message)s')

initIfUninitialized()

def getLogger(name):
    lg = logging.getLogger(name)
    
    level = logging.WARNING
    if settings.isDebug():
        level = logging.DEBUG
    lg.setLevel(level)
    
    return lg