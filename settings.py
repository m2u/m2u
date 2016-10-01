"""
Module for loading and saving user settings.
"""

import os
import ConfigParser

config = ConfigParser.ConfigParser()
thispath = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE_PATH = os.path.join(thispath, 'settings.cfg')

try:
    config.read(CONFIG_FILE_PATH)
except ConfigParser.Error:
    pass


def is_debug():
    try:
        return config.getboolean("General", "Debug")
    except ConfigParser.Error:
        return True


def get_or_default(section, option, default, write_to_file=True):
    """ Try to get the value of `option` in `section`.
    If the setting can not be found, use `default` to set its
    value. If `write` is True, save this to the config file.

    This is to prevent having to write a thousand try-catch around
    everywhere you want to parse a value from the config.
    """
    try:
        return config.get(section, option)
    except ConfigParser.Error:
        if write_to_file:
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, str(default))
        return str(default)


def set_option(section, option, value):
    """ Set the option. If the section does not exist, create it
    automatically.
    """
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)


def save_config():
    with open(CONFIG_FILE_PATH, 'wb') as configfile:
        config.write(configfile)


def get_config_parser():
    return config
