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
        import max
        program = max
    else:
        print("undefined program")

    # create the GUI by loading the .ui file and connecting it to functionality
    from max import maxGUI
    maxGUI.launchGUI()
    
def initEditor(editorName):
    global editor
    import udk
    editor = udk

def alive():
    print("hub hier")

