import sys
program = None
editor= None

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
    load the correct module for the program
    """
    global program
    if programName == "maya":
        from m2u import maya
        program = maya
    elif programName == "max":
        from m2u import max
        program = max
    else:
        print("undefined program")
    

def initEditor(editorName):
    global editor
    from m2u import udk
    editor = udk

def alive():
    print("hub hier")

