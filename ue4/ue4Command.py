""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

"""

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
    msg = ("RenameObject %s %s" % (name, newName))
    ue4Conn.sendMessage(msg)


def duplicateObject(name, dupName, t=None, r=None, s=None):
    """duplicate an object with optional transformations

    :param name: name of the object to modify
    :param dupName: desired name for the duplicate
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change
    
    """
    T = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    R = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    S = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    msg = ("DuplicateObject "+name+" "+dupName+" "+T+" "+R+" "+S)
    ue4Conn.sendMessage(msg)


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
    :return: string, name that is free
    
    """
    pass