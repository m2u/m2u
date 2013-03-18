# this file defines functions for actual commands which interact with UDK
import udkUI


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
# not sure if we should use that...
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

def exportMeshToFile(meshSig, filePath, withTextures=True):
    """
    exports a static mesh by placing it in the map and deleting it after export
    it can export the materials textures as bmp
    filePath must include the filename and extension
    """
    udkUI.callExportSelected(filePath, withTextures)