""" this file defines functions for actual commands which interact with UDK

commands will either be issued by sending console commands to the Editor or by
activating buttons or menu-items in the Editor-UI.
see http://udn.epicgames.com/Three/EditorConsoleCommands.html
and http://udn.epicgames.com/Three/ConsoleCommands.html

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

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

###########################
# #-- helper functions -- #
###########################

# this function should be removed. converting to and from udk rotation is task
# of the udkParser and udkComposer, so that only unrealText has the strange rot
# format, while everywhere else a normal rotation of 360 degree is used
def _convertRotationToUDK(rotTuple):
    """ converts into udk's 65536 for a full rotation format """
    # 182.04444... is 65536.0/360
    newrot=((rotTuple[0]*182.04444444444445)%65536,
            (rotTuple[1]*182.04444444444445)%65536,
            (rotTuple[2]*182.04444444444445)%65536)
    return newrot

def getUnrealTextFromSelection(cut = False):
    pyperclip.setcb("") #make the cb empty
    if cut:
        cutToClipboard()
    else:
        copyToClipboard()
    text = pyperclip.getcb()
    if text == "":
        #print "# m2u debug: could not copy to clipboard"
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
    """add objects to the current selection

    :param namesList: list containing the object names

    """
    for name in namesList:
        command = "ACTOR SELECT NAME="+name
        udkUI.fireCommand(command)

def selectByName(name): 
    """select object, deselect everything else!

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

def _transformObject_old(objName, trans, rot, scale):
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

    You may use the function :func:`getFreeName` to find a name that is unused
    in UDK prior to actually trying to rename the object. You should still
    check the returned value.

    .. warning: UDK will always use the given name, even if an object already
    has that name, as long as the name is valid. The old object will lose it's
    name.

    To make sure other objects don't lose their name, we will first ask
    UDK if the name we want to assign is already taken (we can check that by
    trying to select the object) and return early if it is. If not, we will
    still check if the name we wanted to assign actually ended up that way
    in UDK.
    
    .. warning: UDK seems to have a very non-restrictive name-policy, accepting
    nearly everything you throw at it, although it may break stuff!

    .. seealso:: :func:`getFreeName`
    
    """
    # check if the object we want to rename exists
    selectByName(name) 
    unrtext = getUnrealTextFromSelection(True)
    if unrtext is None:
        #print "Error: no object with name '%s' exists" % name
        _lg.error(("No object with name '%s' exists" % name))
        # TODO: this maybe should not print an error, maybe a warning or only debug?
        return (False, None)
    
    # check if the newName is already taken
    selectByName(newName)
    unrtext = getUnrealTextFromSelection(False)
    if unrtext is not None:
        #print "Error: name '%s' already taken" % newName
        _lg.error("Name '%s' already taken" % newName)
        return (False,None)
    
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
        #print "Error: pasting renamed object failed"
        _lg.error("Pasting renamed object failed")
        # TODO: we might try to paste back the initally cutted object here
        # or let the user hit undo?
        return (False,None)
    
    chkObj = udkParser.parseActor(chktext)
    if chkObj.name == newName:
        # renaming succesfull, yeah!
        return (True,None)
    else:
        # the object was renamed! but the editor changed the name...
        _lg.warn("Rename returned a different name than desired "
               "('%s' instead of '%s')." % (chkObj.name, newName))
        return (False, chkObj.name)


def getObjectInfosFromSelection(cut=False):
    unrtext = getUnrealTextFromSelection(cut)
    if unrtext is None:
       return None
    return  udkParser.parseActors(unrtext)

def getObjectInfoFromName(name, cut=False):
    selectByName(name)
    unrtext = getUnrealTextFromSelection(cut)
    if unrtext is None:
        return None
    return udkParser.parseActor(unrtext)

def getObjectInfosFromNames(nameList, cut=False):
    deselectAll()
    selectByNames(nameList)
    unrtext = getUnrealTextFromSelection(cut)
    if unrtext is None:
        return None
    return udkParser.parseActors(unrtext)


def duplicateObject(name, dupName, t=None, r=None, s=None):
    """ duplicates object with name and assigns dupName to the copy

    :param name: string, object to duplicate
    :param dupName: string, name for the duplicated object
    :param t: translate tuple or None if to take from original
    :param r: rotation tuple or None if to take from original
    :param s: scale tuple or None if to take from original

    :return: tuple (int,string) the int will be
        - 0 if no problem occured
        - 1 if the original object could not be found
        - 2 if the name for the duplicate is already taken
        - 3 if the name was changed by the editor
        - 4 udk error, reason unknown
    if the return value is 3, the string will be the name the Editor
    assigned and None otherwise

    If the return value is 1 or 2, the calling function should change
    the name(s) and try again.
    If the return value is (3,string) the calling function must assign
    the returned name to the original object in the Program or find a new
    fitting name and assign it to the duplicated object using the
    :func:`renameObject` function with the returned string as name.

    .. seealso:: :func:`renameObject` :func:`getFreeName`

    """
    # TODO: this function is very similar to renameObject, maybe common
    # functionality can be delegated to a common function

    # TODO: make checking for old object and free name optional, because
    # this should be handled inside the program before actually calling
    # this function (because they search for a free name anyway)
    # or should they stupidly call this function and make use of the return code
    # instead? (means call getFreeName in here and return that name to the caller)
    # renameObject(name, newName, bSecure = True, bGetBestNameIfNoFit = True)
    #  bSecure = check if name is unused
    #  bGetBestNameblah = let udk find an unused name
    # checking if an object exists in the Program function would be bad, because
    # it creates an unnecessary overhead as we have to "get" the object here anyway
    
    # check if the object we want to duplicate exists
    objInfo = getObjectInfoFromName(name)
    if objInfo is None:
        #print "Error: Duplication failed, original object could not be found."
        _lg.error("Duplication failed, original object could not be found.")
        return (1,None)
        
    # check if the newName is already taken
    selectByName(dupName)
    unrtext = getUnrealTextFromSelection(False)
    if unrtext is not None:
        #print "Error: name '%s' already taken" % dupName
        _lg.error("Name '%s' already taken" % dupName)
        return (2,None)
    
    objInfo.name = dupName
    if t is not None: objInfo.position = t
    if r is not None: objInfo.rotation = r
    if s is not None: objInfo.scale = s
    pasteFromObjectInfoList([objInfo,])
    
    # check if name of pasted object is ok
    # TODO: this maybe optional, because it may take a lot of processing time
    # so maybe give the function a flag to skip this checking?
    # note: udk auto-selects newly pasted objects for us.
    chktext = getUnrealTextFromSelection(False)
    if chktext is None:
        #print "Error: pasting new object failed"
        _lg.error("Pasting new object failed")
        # TODO: we might try to paste back the initally cutted object here
        # or let the user hit undo?
        return (4,None)
    
    chkObj = udkParser.parseActor(chktext)
    if chkObj.name == dupName:
        # renaming succesfull, yeah!
        return (0,None)
    else:
        # the object was renamed! but the editor changed the name...
        _lg.warn("Editor returned a different name than desired "
               "('%s' instead of '%s')." % (chkObj.name, dupName))
        return (3, chkObj.name)


def editExistingObject(name, replObjInfo):
    """
    vermutlich sollte auch transform object umgeschrieben werden auf ein
    editExistingObject(objInfo), wo einfach versucht wird das object das
    bereits existiert mit einem aus dem objInfo erzeugten zu ersetzen
    die gleiche funktin ist dann allgemein nutzbar transform aber auch
    zum setzen von anderen eigenschaften, wie z.b. den genuzten mesh oder so

    das problem ist, von wegen ersetzen, muss ja erstmal das original objekt geholt werden
    wo wird festgelegt, welche attribute ersetzt werden etc? demnach kann das eigentlich nur eine interne funkiton sein, die von doch spezialisierten (auf transformation etc) funktionen aufgerufen wird
    """
    pass


def transformObject(objName, t=None, r=None, s=None):
    """transform an object with absolute transformations.

    :param objName: name of the object to modify
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change

    Transforms an object by cutting it from the level,
    replacing parameters and pasting the changed object back
    to the level.
    
    """
    objInfo = getObjectInfoFromName(objName, True)
    if objInfo is None:
        #print "Error: no object with name %s found." % objName
        return
        
    if t is not None: objInfo.position = t
    if r is not None: objInfo.rotation = r
    if s is not None: objInfo.scale = s
    pasteFromObjectInfoList([objInfo,])


def getFreeName(name, maxIters = 5000):
    """ check if the name is in use, if it is, return the next
    unused name by increasing (or adding) the number-suffix

    :param name: the basic name, to check
    :param maxIters: the maximum number of name-checks to perform
    :return: string, name that is free
    
    """
    # check if the name is still free
    selectByName(name)
    unrtext = getUnrealTextFromSelection(False)
    if unrtext is None:
        _lg.debug("name %s is free" % name)
        return name
    # name was not free, so we need to create a new one and check again
    _lg.debug("name: %s is not free" % name)
    
    # split name into name and suffix
    g = re.match("(.+?)(\d*)$",str(name))
    rawName = g.group(1)
    hasSuffix = len(g.group(2))>0
    suffix = int(g.group(2)) if hasSuffix else 0

    iters = 0
    while True:
        # increase suffix and check if that newName is already taken
        suffix += 1
        iters += 1
        newName = rawName + str(suffix)
        _lg.debug("udk checking "+newName)
        deselectAll() # make sure really NOTHING is selected, sometimes shit happens
        selectByName(newName)
        unrtext = getUnrealTextFromSelection(False)
        if unrtext is None:
            # name is free
            return newName
        # name is not free, continue loop until a name is found ;)
        if iters > maxIters:
            _lg.error("tried %d iterations, could not find a name, cancelling"
                      % iters )
            return None
