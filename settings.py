"""
for loading and saving user settings
"""

import os
import ConfigParser
import m2u

config = ConfigParser.ConfigParser()
m2upath = os.path.dirname(os.path.realpath(__file__))

try:
    config.read(m2upath+'/settings.cfg')
except ConfigParser.Error:
    pass

def isDebug():
    try:
        return config.getboolean("General","Debug")
    except ConfigParser.Error:
        #return m2u.isDebugMode()
        return True


def getAndSetValueDefaultIfError(section, option, defaultstr, write=True):
    """ try to get the value of `option` in `section`
    if that fails, return the provided defaultstr and
    at the same time set the provided defaultstr to be saved
    out in a future save of the config file, if write is True.

    This is to prevent having to write a thousand try-catch around
    everywhere you want to parse a value from the config.
    """
    try:
        return config.get(section, option)
    except ConfigParser.Error:
        if write:
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, defaultstr)
        return defaultstr

def setOptionCreateSection(section, option, value):
    """ set the option, if the section does not exist, create it automatically
    """
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)

def saveConfig():
    with open(m2upath+'/settings.cfg', 'wb') as configfile:
        config.write(configfile)

def getConfigParser():
    return config