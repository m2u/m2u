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

#-- helper functions --
def _convertRotationToUDK(rotTuple):
    # fucking tuples are immutable
    newrot=((rotTuple[0]*182.04444)%65536, (rotTuple[1]*182.04444)%65536, (rotTuple[2]*182.04444)%65536)
    return newrot

#-- command functions --
def setCamera(x,y,z,rx,ry,rz):
    rot=_convertRotationToUDK((rx,ry,rz))
    command = "BUGITGO %f %f %f %f %f %f" % (x,y,z,rot[0],rot[1],rot[2])   
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
    transforms an object by cutting it from the level,
    replacing parameters and pasting the changed text to the level
    objName is only the instance name
    trans rot and scale are float tuples (f,f,f)
    """
    rot = _convertRotationToUDK(rot)
    selectByName(objName)
    time.sleep(0.1) # WAIT
    #keep = pyperclip.getcb() #backup current clipboard TODO: reenable
    pyperclip.setcb("") #make the cb empty for while loop
    cutToClipboard() # this will be executed somewhen, we don't know when
    time.sleep(0.1) # WAIT
    #old = ""
    #while old == "": # so we wait until the clipboard is filled by it
    #    time.sleep(0.01)
    # this loop might be an option, but it took forever, maybe we block
    # some execution speed when doing this or so?
    old = pyperclip.getcb()
    # we assume that transformation order is alwasy location, rotation, scale!
    locInd = str.find(old,"Location=(")
    assert locInd is not -1, "no Location attribute found, there is currently no solution implemented for that case." # TODO we don't know where to add it in that case, so leave it be for now
    lastInd = locInd #index of the last translate information found
    nextInd = str.find(old,"Rotation=(",locInd)
    if nextInd is not -1: #found rotation as next, save the index
        lastInd = nextInd
    nextInd = str.find(old,"DrawScale3D=(",nextInd)
    if nextInd is not -1: #found scale as next, save the index
        lastInd = nextInd
    #now we remove the transformation block from the text   
    endInd = str.find(old,"\n",nextInd) + 1 # end of last statement
    part1 = old[0:locInd] #the part before the transform stuff
    part2 = old[endInd:] #the part after the transform stuff
    #create our own transformation block
    locRep = "Location=(X=%f,Y=%f,Z=%f)" % trans
    rotRep = "Rotation=(Pitch=%d,Yaw=%d,Roll=%d)" % rot
    scaleRep = "DrawScale3D=(X=%f,Y=%f,Z=%f)" % scale
    #add them all together as a new object string
    new = part1 + locRep + "\n" + rotRep + "\n" + scaleRep + "\n" + part2
    print new
    
    """
    locPat = r"Location=\(.*?\)" # match location line regex
    locRep = "Location=(X=%f,Y=%f,Z=%f)" % trans
    new = re.sub(locPat, locRep, old, 1)
    assert new is not None, "no Location attribute found, there is currently no solution implemented for that case." # TODO we don't know where to add it in that case, so leave it be for now
    # TODO: rotate and scale are always after translate, in specific order. therefore, find the line in which the LOCATION is, and go on from there, might be faster than using the sub two times over again.
    old = new
    rotPat = r"Rotation=\(.*?\)" # match rotation line regex
    rotRep = "Rotation=(Pitch=%f,Yaw=%f,Roll=%f)" % rot
    new = re.sub(rotPat, rotRep, old, 1)
    if new is None: # no rotation line yet in text
        new += rotRep + "/n"
        
    scalePat = r"DrawScale3D=\(.*?\)" # match scale line regex
    scaleRep = "DrawScale3D=(X=%f,Y=%f,Z=%f)" % scale
    new = re.sub(scalePat, scaleRep, new, 1)
    if new is None: # no scale line yet in text
        new += scaleRep + "/n"
        
    #print "new " +new
    """
    pyperclip.setcb(new)
    pasteFromClipboard()
    #here we would have to wait long enough again for ued to finish,
    # before resetting the clipboard.
    # TODO: find a sync-wait-whatever function from windows
    #pyperclip.setcb(keep) #restore original clipboard