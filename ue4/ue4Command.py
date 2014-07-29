""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

"""

import os

from m2u.helper.ObjectInfo import ObjectInfo
from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def transformObject(objName, t=None, r=None, s=None):
    """transform an object with absolute transformations.

    :param objName: name of the object to modify
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change
    
    """
    T = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    R = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    S = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    msg = ("TransformObject "+objName+" "+T+" "+R+" "+S)
    ue4Conn.sendMessage(msg)


def transformCamera( x,y,z, rx,ry,rz, CamIdentifier="All"):
    """Set the Camera in UEd

    :param x,y,z: position for the camera
    :param rx,ry,rz: rotation for the camera
    :param CamIdentifier: string that explains which viewports to set

    By default, all Viewport Cameras will be set to the provided position and
    rotation.

    """
    #TODO: CamIdentifier is not yet used in m2uPlugin, possible values should be:
    #All, AllPersp, AllTop, AllFront, AllSide, or an Index specifying a specific
    #viewport. Or a name for a camera?
    msg = ("TransformCamera %f %f %f %f %f %f %s" % \
           (x,y,z,rx,ry,rz,CamIdentifier))
    ue4Conn.sendMessage(msg)


def deleteSelected():
    msg = ("DeleteSelected")
    ue4Conn.sendMessage(msg)


def renameObject(name, newName):
    """try to assign a new name to an object.

    :param name: current name of the object
    :param newName: desired name for the object

    :return: tuple (bool,string) True if no problem occured, False otherwise
    if False, the string will be the name the Editor assigned or None if no
    renaming took place.

    You can use :func:`getFreeName` to find a name that is unused in the
    Editor prior to actually renaming the object.
    """
    msg = ("RenameObject %s %s" % (name, newName))
    result = ue4Conn.sendMessage(msg)
    if result =="1":
        _lg.error(("No object with name '%s' exists" % name))
        # TODO: this maybe should not print an error, maybe a warning or only debug?
        return (False, None)
    if result == newName:
        return (True, None)
    else:
        # the object was (probably) renamed! but the editor changed the name...
        _lg.warn("Rename returned a different name than desired "
               "('%s' instead of '%s')." % (result, newName))
        return (False, result)


# TODO: implement a batch duplicate function for UE and the appropriate
# caller in maya
def duplicateObject(name, dupName, t=None, r=None, s=None):
    """duplicate an object with optional transformations

    :param name: name of the object to modify
    :param dupName: desired name for the duplicate
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change

    :return: tuple (int,string) the int will be
        - 0 if no problem occured
        - 1 if the original object could not be found
        - 2 if the name for the duplicate is already taken
        - 3 if the name was changed by the editor
        - 4 error, reason unknown
    Return values 2 and 3 are mutually exclusive by implementation.
    If 3 is returned, the string will be the name the Editor assigned
    and None otherwise.

    If the return value is 1 or 2, the calling function should change
    the name(s) and try again.
    If the return value is (3,string) the calling function must assign
    the returned name to the original object in the Program or find a new
    fitting name and assign it to the duplicated object using the
    :func:`renameObject` function with the returned string as name.

    .. seealso:: :func:`renameObject` :func:`getFreeName`
    
    """
    T = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    R = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    S = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    msg = ("DuplicateObject "+name+" "+dupName+" "+T+" "+R+" "+S)
    result = ue4Conn.sendMessage(msg)
    vals = result.split()
    rval = int(vals[0])
    rname = None
    if len(vals)>1:
        rname = vals[1]
        
    if rval == 1:
        _lg.error("Duplication failed, original object could not be found.")
    elif rval == 3:
        _lg.warn("Editor returned a different name than desired "
               "('%s' instead of '%s')." % (rname, dupName))
    return (rval, rname)


def undo():
    msg = ("Undo")
    ue4Conn.sendMessage(msg)


def redo():
    msg = ("Redo")
    ue4Conn.sendMessage(msg)


def getFreeName(name, maxIters=5000):
    """ check if the name is in use, if it is, return the next
    unused name by increasing (or adding) the number-suffix

    :param name: the basic name, to check
    :param maxIters: the maximum number of name-checks to perform
    (maxIters currently not used in UE4)
    
    :return: string, name that is free
    
    """
    msg = ("GetFreeName "+name)
    result = ue4Conn.sendMessage(msg)
    return result;


def deleteObject(name):
    """ try to delete the object, no return code
    """
    msg = ("DeleteObject "+name)
    ue4Conn.sendMessage(msg)


def parentChildTo(childName, parentName):
    """ set the parent of childName to be parentName

    if parentName is an empty string or None, will parent to the world

    """
    msg = ("ParentChildTo "+childName)
    if (parentName is not None) and (parentName !=''):
        msg = msg + " " + parentName
    
    ue4Conn.sendMessage(msg)


def addActorBatch(assetList):
    """ add an actor to the level for each entry in the assetList
    each value in the List has to be an `ObjectInfo` object.
    """
    msg = 'AddActorBatch'
    for objInfo in assetList:
        line = objectInfoToString(objInfo)
        msg = msg +"\n" + line
    _lg.debug("assembled add batch command: "+msg)
    ue4Conn.sendMessage(msg)


def objectInfoToString(objInfo):
    """ convert an ObjectInfo object into a one-line string as used by
    our UE4-interpreter.
    
    """
    t = objInfo.pos
    r = objInfo.rot
    s = objInfo.scale
    T = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    R = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    S = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    assP = internalAssetPathFromAssetFilePath(objInfo.AssetPath)
    text = assP+" "+objInfo.name+" "+T+" "+R+" "+S
    return text

def internalAssetPathFromAssetFilePath(assetPath):
    rpath,ext = os.path.splitext(assetPath)
    if not rpath.startswith("/") and len(rpath)>0:
        rpath = "/"+rpath
    assP = "/Game"+rpath
    assP.replace("//","/")
    return assP