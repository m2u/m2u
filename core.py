
"""
the window to the world.

The core module is the only reference other systems (like the UI) should need
to know. To access the actual program or editor interfaces, get the 
module by calling :func:`getProgram` and :func:`getEditor`. 

"""

import os
import m2u
from m2u import logger as _logger
_lg = _logger.getLogger(__name__)
import m2u.settings as settings

def getM2uBasePath():
    """ get the path to the m2u folder (the folder this file is in)
    """
    fpath = os.path.abspath(__file__)
    fdir = os.path.dirname(fpath)
    return fdir


_program = None
_editor = None
_pipeline = None

def getProgram():
    """get the program module"""
    return _program

def getEditor():
    """get the editor module"""
    return _editor

def getPipeline():
    """get the pipeline module"""
    return _pipeline

def initialize(programName,editorName="udk"):
    """Initializes the whole m2u system.
    
    :param programName: the program to use 'max' or 'maya'
    :param editorName: the target engine to use
    
    """
    _initProgram(programName)
    _initEditor(editorName)
    _initPipeline()

def _initProgram(programName):
    """Load the correct module as program."""
    global _program
    try:
        #_program = __import__("m2u."+programName)
        _program = __import__('m2u.'+programName, globals(), locals(),
                              ["__name__"], -1)
        _lg.info( "Program module is `"+_program.__name__+"`")
    except ImportError:
        _lg.error("Unable to import program module %s" % (programName,))

def _initEditor(editorName):
    """load the module for the editor"""
    global _editor
    try:
        _editor = __import__('m2u.'+editorName, globals(), locals(),
                              ["__name__"], -1)
        _lg.info( "Editor module is `"+_editor.__name__+"`")
    except ImportError:
        _lg.error("Unable to import editor module %s" % (editorName,))


def _initPipeline():
    """load and use the pipeline module that is set in the settings file.
    If not set, use the m2u-minimal-pipeline instead.

    """
    global _pipeline
    name = "m2u.pipeline" # the fallback mini pipe
    
    if settings.config.has_option("General", "PipelineModule"):
        name = settings.config.get("General", "PipelineModule")
    
    try:
        _pipeline = __import__(name, globals(), locals(),
                             ["__name__"], -1)
        _lg.info( "Pipeline module is `"+_pipeline.__name__+"`")
    except ImportError:
        _lg.error("Unable to import pipeline module %s" % (name,))
