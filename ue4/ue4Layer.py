""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

commands for Display Layers

"""

from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

# TODO: maybe print some warning if the layer could not be found
# maybe we should give the option to auto-generate layers if not found?

def addObjectToLayer(objName, layerName, removeFromOthers=True):
    msg = ("AddObjectToLayer "+objName+" "+layerName+" "+removeFromOthers)
    return ue4Conn.sendMessage(msg)


def removeObjectFromLayer(objName, layerName):
    msg = ("RemoveObjectFromLayer "+objName+" "+layerName)
    return ue4Conn.sendMessage(msg)


def removeObjectFromAllLayers(objName):
    msg = ("RemoveObjectFromAllLayers "+objName)
    return ue4Conn.sendMessage(msg)


def createLayer(layerName):
    msg = ("CreateLayer "+layerName)
    return ue4Conn.sendMessage(msg)


# NOTE: deleting layers is done via the normal delete-object function for now
#def deleteLayer(layerName):
#    msg = ("DeleteLayer "+layerName)
#    return ue4Conn.sendMessage(msg)


def hideLayer(layerName):
    msg = ("HideLayer "+layerName)
    return ue4Conn.sendMessage(msg)


def unhideLayer(layerName):
    msg = ("UnhideLayer "+layerName)
    return ue4Conn.sendMessage(msg)