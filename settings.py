"""
for loading and saving user settings
"""

import os
import ConfigParser

config = ConfigParser.ConfigParser()
m2upath = os.path.dirname(os.path.realpath(__file__))


def isDebug():
    return True