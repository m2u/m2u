#NOTE: NOT USED ANYMORE

import sys
program = None
editor = None

def initialize(programName,editorName="udk"):
    """
    
    Arguments:
    - `program`: the program to use 'max' or 'maya'
    - `editor`: the target engine to use currently only 'udk'
    """
    initProgram(programName)
    initEditor(editorName)

def initProgram(programName):
    """
    Load the correct module for the program
    """
    global program
    
    if programName == "maya":
        from m2u import maya
        program = maya

    elif programName == "max":
        from m2u import max
        reload(max) # for testing
        # create the GUI by loading the .ui file and connecting it to functionality
        from max import maxGUI
        reload(maxGUI)
        maxGUI.launchGUI()
        program = max
    else:
        print("undefined program")

def initEditor(editorName):
    global editor
    from m2u import udk
    editor = udk
    print "EDI:", editor

def alive():
    print("hub hier")

