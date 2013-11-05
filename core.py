# the actual m2u module file
# information herein should be the only reference all other files should need to know.


# this is the core of m2u the only and first module to be imported and initialize called from the program specific startup scripts

import os

def getTempFolder():
    #this function may be changed to return a user-defined folder
    return os.getenv("TEMP")

__program = None
__editor = None

def getProgram():
    """get the program module"""
    return __program

def getEditor():
    """get the editor module"""
    return __editor

def initialize(programName,editorName="udk"):
    """Initializes the whole m2u system.
    
    :param programName: the program to use 'max' or 'maya'
    :param editorName: the target engine to use currently only 'udk'
    
    """
    initProgram(programName)
    initEditor(editorName)

def initProgram(programName):
    """Load the correct module as program."""
    global __program
    
    # if programName == "maya":
    #     import maya
    #     __program = maya
    
    # elif programName == "max":
    #     import max
    #     __program = max
    # else:
    #     print("# m2u: undefined program")
    
    try:
        __program = __import__(programName)
    except ImportError:
        print "Unable to import program module %s" % (programName,)

def initEditor(editorName):
    """load the module for the editor"""
    global __editor
    import udk
    __editor = udk

