# the actual m2u module file
# information herein should be the only reference all other files should need to know.


# this is the core of m2u the only and first module to be imported and initialize called from the program specific startup scripts

__program = None
__editor = None

def getProgram():
    global __program
    return __program

def getEditor():
    global __editor
    return __editor

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
    global __program
    
    if programName == "maya":
        import maya
        __program = maya

    elif programName == "max":
        import max
        reload(max) # for testing
        # create the GUI by loading the .ui file and connecting it to functionality
        from max import maxGUI
        reload(maxGUI)
        maxGUI.launchGUI()
        __program = max
    else:
        print("undefined program")

    print "PROG:", __program

def initEditor(editorName):
    global __editor
    import udk
    __editor = udk
    print "EDI:", __editor

def alive():
    print("m2u module (hub) is alive")

