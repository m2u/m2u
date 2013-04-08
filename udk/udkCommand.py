# this file defines functions for actual commands which interact with UDK
import udkUI
#import Tkinter
import pyperclip
import re
import time
"""
DELETE - Deletes the selected actors. # 
DUPLICATE - Duplicates the selected actors. 
"""
#see http://udn.epicgames.com/Three/EditorConsoleCommands.html


def setCamera(x,y,z,rx,ry,rz):
    command = "BUGITGO %f %f %f %f %f %f" % (x,y,z,rx,ry,rz)   
    udkUI.fireCommand(command)

#SELECT - General selection commands 
#    BUILDERBRUSH - Selects the builder brush. 
#    NONE - Deselects all actors.
#    SELECTNAME [NAME=name] - Select actors with names matching the given name.
#ACTOR
#    SELECT NAME= - Select the actor with the given name.
def deselectAll():
    command = "SELECT NONE"
    udkUI.fireCommand(command)

def selectByNames(names):
    #actor select adds to selection
    for name in names:
        command = "ACTOR SELECT NAME="+name
        udkUI.fireCommand(command)

def selectByName(name):
    command = "SELECT SELECTNAME NAME="+name
    udkUI.fireCommand(command)


#TRANSACTION - Undo and redo commands 
#    REDO - Performs the last undone operation. 
#    UNDO - Undoes the last performed operation.
# !! not sure if we should use that... !!
def redo():
    command = "TRANSACTON REDO"
    udkUI.fireCommand(command)

def undo():
    command = "TRANSACTION UNDO"
    udkUI.fireCommand(command)

#EDIT - General editing commands 
#    COPY - Copy the selection to the clipboard. 
#    CUT - Cut the selection to the clipboard. 
#    PASTE [TO=location] - Paste clipboard contents into the map. The location can be: 
#        HERE - Pastes the clipboard contents to the mouse location. 
#        ORIGIN - Pastes the clipboard contents to the world origin.
def copyToClipboard():
    command = "EDIT COPY"
    udkUI.fireCommand(command)

def cutToClipboard():
    command = "EDIT CUT"
    udkUI.fireCommand(command)

def pasteFromClipboard():
    command = "EDIT PASTE" #no TO= preserves positions
    udkUI.fireCommand(command)

#OBJ - General object commands 
#    EXPORT [PACKAGE=package] [TYPE=type] [FILE=file] [NAME=name] - Export the object of the given type with the given name to the specified file. 
#    RENAME [OLDPACKAGE=oldpackage] [OLDGROUP=oldgroup] [OLDNAME=oldname] [NEWPACKAGE=newpackage] [NEWGROUP=newgroup] [NEWNAME=newname] - Renames the object matching the old package, old group, and old name to the new package, new group, and new name. 
#    SAVEPACKAGE [FILE=file] [PACKAGE=package] - Save the given package to the specified file.

def exportObjToFile(package, objName, objType, filePath):
    """
    all parameters are strings, package is only the package name, no groups
    filePath must include the filename and extension
    """
    command = "OBJ EXPORT PACKAGE=%s TYPE=%s FILE=%s NAME=%s" % \
              (package, objType, filePath, objName)
    udkUI.fireCommand(command)

def exportMeshToFile(meshSig, folder, fileName, withTextures=True):
    """
    exports a static mesh by placing it in the map and deleting it after export
    it can export the materials textures as bmp
    meshSig is the fully qualified mesh name (package.groups.mesh)
    """
    udkUI.callExportSelected(folder, withTextures)

def transformObject(objName, trans, rot, scale):
    """
    objName is only the instance name
    trans rot and scale are float tuples
    """
    selectByName(objName)
    time.sleep(0.1) # WAIT
    keep = pyperclip.getcb() #backup current clipboard
    pyperclip.setcb("") #make the cb empty for while loop
    cutToClipboard() # this will be executed somewhen, we don't know when
    time.sleep(0.1) # WAIT
    old = ""
    #while old == "": # so we wait until the clipboard is filled by it
    #    time.sleep(0.01)
    # this loop might be an option, but it took forever, maybe we block
    # some execution speed when doing this or so?
    old = pyperclip.getcb()
    # [-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)? # float regex
    print "old " +old
    locPat = r"Location=\(.*?\)" # match location line regex
    locRep = "Location=(X=%f,Y=%f,Y=%f)" % trans
    new = re.sub(locPat, locRep, old, 1)
    print "new " +new
    pyperclip.setcb(new)
    pasteFromClipboard()
    #here we would have to wait long enough again for ued to finish,
    # before resetting the clipboard.
    # TODO: find a sync-wait-whatever function from windows
    #pyperclip.setcb(keep) #restore original clipboard