"""
The window to the world.

The core module is the only reference other systems (like the UI)
should need to import.
"""

import os
import sys
import logging

from . import settings
from . import logger

logger.init_if_uninitialized()

_lg = logging.getLogger(__name__)

this = sys.modules[__name__]

this.program = None
this.editor = None
this.pipeline = None


def get_m2u_base_path():
    """ Get the path to the m2u folder (the folder this file is in)
    """
    fpath = os.path.abspath(__file__)
    fdir = os.path.dirname(fpath)
    return fdir


def initialize(program_name, editor_name):
    """Initializes the whole m2u system.

    :param program_name: the program to use ('max' or 'maya' etc.)
    :param editor_name: the target engine to use ('ue4', 'unity' etc.)

    """
    if not program_name:
        _lg.error("No program module specified for initialization. "
                  "Make sure to pass the program name to your initialize call."
                  )
        return
    if not editor_name:
        _lg.error("No editor module specified for initialization. "
                  "Make sure to pass the editor name to your initialize call.")
        return
    _init_program(program_name)
    _init_editor(editor_name)
    _init_pipeline()


def _init_program(program_name):
    """Load the correct module as program."""
    try:
        this.program = __import__('m2u.' + program_name, globals(), locals(),
                                  ["__name__"], -1)
        _lg.info("Program module is `{0}`".format(this.program.__name__))
    except ImportError:
        _lg.error("Unable to import program module {0}".format(program_name))
        raise


def _init_editor(editor_name):
    """Load the module for the editor."""
    try:
        this.editor = __import__('m2u.' + editor_name, globals(), locals(),
                                 ["__name__"], -1)
        _lg.info("Editor module is `{0}`".format(this.editor.__name__))
    except ImportError:
        _lg.error("Unable to import editor module {0}".format(editor_name))
        raise


def _init_pipeline():
    """Load and use the pipeline module that is set in the settings file.
    If not set, use the m2u-minimal-pipeline instead.
    """
    name = "m2u.pipeline"  # The fallback mini-pipeline module

    if settings.config.has_option("General", "PipelineModule"):
        name = settings.config.get("General", "PipelineModule")

    try:
        this.pipeline = __import__(name, globals(), locals(),
                                   ["__name__"], -1)
        _lg.info("Pipeline module is `{0}`".format(this.pipeline.__name__))
    except ImportError:
        _lg.error("Unable to import pipeline module {0}".format(name))
        raise
