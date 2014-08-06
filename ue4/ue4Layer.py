""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

commands for Display Layers


An Object can always only be member of one Layer. This is not a restriction by UE4
which allows objects to be in multiple layers, but a restriction of how many other
programs work with display layers (Maya, Unity).
Since our main interest currently is Maya as the Program, we will not allow any other
behaviour here.

"""

from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def addObjectsToLayer(layerName, objList, removeFromOthers=True):
    """ add objects in list to that layer, remove them from all other layers.
    If the layer does not exist, it will be created.
    """
    names = "["+(','.join(objList))+"]"
    msg = ("AddObjectsToLayer "+layerName+" "+names+
           " RemoveFromOthers="+str(removeFromOthers))
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)


#def removeObjectFromLayer(objName, layerName):
#    msg = ("RemoveObjectFromLayer "+objName+" "+layerName)
#    return ue4Conn.sendMessage(msg)


def removeObjectsFromAllLayers(objList):
    names = "["+(','.join(objList))+"]"
    msg = ("RemoveObjectsFromAllLayers "+names)
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)


def renameLayer(oldName, newName):
    msg = ("RenameLayer "+oldName+" "+newName)
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)

#def createLayer(layerName):
#    msg = ("CreateLayer "+layerName)
#    return ue4Conn.sendMessage(msg)


def deleteLayer(layerName):
    msg = ("DeleteLayer "+layerName)
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)


def hideLayer(layerName):
    msg = ("HideLayer "+layerName)
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)


def unhideLayer(layerName):
    msg = ("UnhideLayer "+layerName)
    print "msg is: "+msg
    return ue4Conn.sendMessage(msg)