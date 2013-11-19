""" this file defines functions for actual commands which interact with UDK

commands will either be issued by sending console commands to the Editor or by
activating buttons or menu-items in the Editor-UI.
see http://udn.epicgames.com/Three/EditorConsoleCommands.html

Functionality for interaction with the UI is found in :mod:`udkUI`

"""

import re
import time

try:
    import pyperclip
except ImportError:
    from . import pyperclip

from m2u.udk import udkUI
from m2u.udk import udkParser
from m2u.udk import udkComposer

###########################
# #-- helper functions -- #
###########################

def _convertRotationToUDK(rotTuple):
    """ converts into udk's 65536 for a full rotation format """
    newrot=((rotTuple[0]*182.04444)%65536, (rotTuple[1]*182.04444)%65536,
            (rotTuple[2]*182.04444)%65536)
    return newrot

def getUnrealTextFromSelection(cut = False):
    pyperclip.setcb("") #make the cb empty
    if cut:
        cutToClipboard()
    else:
        copyToClipboard()
    text = pyperclip.getcb()
    if text == "":
        print "# m2u debug: could not copy to clipboard"
        return None
    return text

############################
# #-- command functions -- #
############################
    
def setCamera(x,y,z,rx,ry,rz):
    """Set the Camera in UDK

    :param x,y,z: position for the camera
    :param rx,ry,rz: rotation for the camera

    By telling UDK to set the camera, all viewport cameras will be set to the
    provided position and rotation, there is no option to set a specific camera
    only.

    """
    rot=_convertRotationToUDK((rx,ry,rz))
    command = "BUGITGO %f %f %f %f %f %f" % (x,y,z,rot[0],rot[1],rot[2])   
    udkUI.fireCommand(command)

def deselectAll():
    #command = "SELECT NONE"
    #udkUI.fireCommand(command)
    udkUI.callSelectNone() #uses the menu instead of command field

def selectByNames(namesList):
    """add provided objects to the current selection

    :param namesList: list containing the object names

    """
    for name in namesList:
        command = "ACTOR SELECT NAME="+name
        udkUI.fireCommand(command)

def selectByName(name): 
    """select provided object, deselect everything else!

    :param name: name of the object to select

    """
    command = "SELECT SELECTNAME NAME="+name
    udkUI.fireCommand(command)



# !! not sure if we should use that, it could cause desyncs !!
def redo():
    command = "TRANSACTON REDO"
    udkUI.fireCommand(command)

def undo():
    command = "TRANSACTION UNDO"
    udkUI.fireCommand(command)

   
def deleteSelected():
    udkUI.callEditDelete() #uses the menu instead of command field
   
def duplicateSelected():
    udkUI.callEditDuplicate() #uses the menu instead of command field


def copyToClipboard():
    #command = "EDIT COPY"
    #udkUI.fireCommand(command)
    udkUI.callEditCopy() #uses the menu instead of command field

def cutToClipboard():
    #command = "EDIT CUT"
    #udkUI.fireCommand(command)
    udkUI.callEditCut() #uses the menu instead of command field
    #udkUI.sendEditCut() #uses keyboard input stream

def pasteFromClipboard():
    #command = "EDIT PASTE" #no TO= preserves positions
    #udkUI.fireCommand(command)
    udkUI.callEditPaste() #uses the menu instead of command field
    #udkUI.sendEditPaste() #uses keyboard input stream


def exportObjToFile(package, objName, objType, filePath):
    """all parameters are strings, package is only the package name, no groups
    filePath must include the filename and extension

    :deprecated: this only works if the resources can be found under their
    original import path, a real export won't work that way 
    """
    command = "OBJ EXPORT PACKAGE=%s TYPE=%s FILE=%s NAME=%s" % \
              (package, objType, filePath, objName)
    udkUI.fireCommand(command)

def exportMeshToFile(meshSig, filePath, withTextures=True):
    """ exports a single static mesh.

    :param meshSig: the fully qualified mesh name (package.groups.mesh)
    :param filePath: the complete path of the file where to export to
    :param withTextures: export materials as Textures, works only if export is obj

    Exports the mesh by placing it in the map and deleting it after export
    it can export the materials textures as bmp
    
    """
    #TODO: do the stuff
    udkUI.callExportSelected(folder, withTextures)

def exportSelectedToFile(filePath, withTextures=True):
    """exports the current selection into a file

    :param filePath: the complete path of the file where to export to
    :param withTextures: export materials as Textures, works only if export is obj

    """
    udkUI.callExportSelected(filePath, withTextures)

def transformObject(objName, trans, rot, scale):
    """transform an object with absolute transformations.

    :param objName: name of the object to modify
    :param trans: translation float tuple
    :param rot: rotation float tuple
    :param scale: 3d scale float tuple

    Transforms an object by cutting it from the level,
    replacing parameters and pasting the changed text to the level
    
    """
    rot = _convertRotationToUDK(rot)
    selectByName(objName)
    
    #keep = pyperclip.getcb() #backup current clipboard TODO: reenable
    pyperclip.setcb("") #make the cb empty for while loop
    cutToClipboard() # this will be executed somewhen, we don't know when
    old = pyperclip.getcb()
    if old == "":
        print "# m2u: could not copy to clipboard"
        return
    # we assume that transformation order is alwasy location, rotation, scale!
    locInd = str.find(old,"Location=(")
    assert locInd is not -1, ("# m2u: No Location attribute found, there is "
                            "currently no solution implemented for that case.")
    # TODO we don't know where to add it in that case, so leave it be for now
    
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
    #print new
    
    pyperclip.setcb(new)
    pasteFromClipboard()
    #pyperclip.setcb(keep) #restore original clipboard

def hideSelected():
    udkUI.callHideSelected()

def unhideAll():
    udkUI.callShowAll()

def isolateSelected():
    udkUI.callIsolateSelected()


def unhideSelected():
    command = "ACTOR UNHIDE SELECTED" # TODO: cmd does not work
    udkUI.fireCommand(command)

def pasteFromObjectInfoList(objInfoList):
    ntext = udkComposer.unrTextFromObjects(objInfoList)
    pyperclip.setcb(ntext)
    pasteFromClipboard()
    # TODO: maybe restore original clipboard text?

def renameObject(name, newName):
    """try to assign a new name to an object.

    :param name: current name of the object
    :param newName: desired name for the object

    :return: tuple (bool,string) True if no problem occured, False otherwise
    if False, the string will be the name the Editor assigned or None if no
    renaming took place

    The problem with assigning new names to objects is, that the desired name
    may already be in use or otherwise invalid. This function will TRY to rename
    an object and check the name that the Editor actually assigned. If they are
    the same, None is returned, if they differ, the actual Editor-created name
    is returned. It is your responsibility to handle this discrepancy then by
    either trying to rename again with another name, assigning the returned name
    to the object in the Program, informing the user that he must enter another
    name etc.

    .. note: UDK will always use the given name, even if an object already has
    that name, as long as the name is valid. The old object will lose it's
    name.

    To make sure other objects don't lose their name, we will first ask
    UDK if the name we want to assign is already taken (we can check that by
    trying to select the object) and return early if it is. If not, we will
    still check if the name we wanted to assign actually ended up that way
    in UDK.
    
    .. note: UDK seems to have a very non-restrictive name-policy, accepting
    nearly everything you throw at it, although it may break stuff!
    
    """
    # check if the newName is already taken
    selectByName(newName)
    unrtext = getUnrealTextFromSelection(False)
    if unrtext is not None:
        print "Error: name '%s' already taken" % newName
        return (False,None)
    
    # check if the object we want to rename exists
    selectByName(name) 
    unrtext = getUnrealTextFromSelection(True)
    if unrtext is None:
        print "Error: no object with name '%s' exists" % name
        return (False, None)
    
    # change name and paste back to Udk
    objInfo = udkParser.parseActor(unrtext)
    objInfo.name = newName
    pasteFromObjectInfoList([objInfo,])
    
    # check if name of pasted object is ok
    # TODO: this maybe optional, because it may take a lot of processing time
    # so maybe give the function a flag to skip this checking?
    # note: udk auto-selects newly pasted objects for us.
    chktext = getUnrealTextFromSelection(False)
    if chktext is None:
        print "Error: pasting renamed object failed"
        # TODO: we might try to paste back the initally cutted object here
        # or let the user hit undo?
        return (False,None)
    
    chkObj = udkParser.parseActor(chktext)
    if chkObj.name == newName:
        # renaming succesfull, yeah!
        return (True,None)
    else:
        # the object was renamed! but the editor changed the name...
        print ("Warning: rename returned a different name than desired "
               "('%s' instead of '%s')." % (chkObj.name, newName))
        return (False, chkObj.name)










