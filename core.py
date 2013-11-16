
"""
the window to the world.

The core module is the only reference other systems (like the UI) should need
to know. To access the actual program or editor interfaces, get the 
module by calling :func:`getProgram` and :func:`getEditor`. 

"""

import os
import m2u

def getTempFolder():
    #this function may be changed to return a user-defined folder
    return os.getenv("TEMP")

_program = None
_editor = None

def getProgram():
    """get the program module"""
    return _program

def getEditor():
    """get the editor module"""
    return _editor

def initialize(programName,editorName="udk"):
    """Initializes the whole m2u system.
    
    :param programName: the program to use 'max' or 'maya'
    :param editorName: the target engine to use currently only 'udk'
    
    """
    _initProgram(programName)
    _initEditor(editorName)

def _initProgram(programName):
    """Load the correct module as program."""
    global _program
    try:
        #_program = __import__("m2u."+programName)
        _program = __import__('m2u.'+programName, globals(), locals(),
                              ["__name__"], -1)
        print "program is "+_program.__name__
    except ImportError:
        print "Unable to import program module %s" % (programName,)

def _initEditor(editorName):
    """load the module for the editor"""
    global _editor
    import m2u.udk as udk
    _editor = udk

