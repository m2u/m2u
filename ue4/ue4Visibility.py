""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

"""

from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def hideSelected():
    """hide currently selected objects
    """
    msg = "HideSelected"
    ue4Conn.sendMessage(msg)


def unhideSelected():
    """show currently selected objects
    """
    msg = "UnhideSelected"
    ue4Conn.sendMessage(msg)


def isolateSelected():
    """hide all but the currently selected objects
    """
    msg = "IsolateSelected"
    ue4Conn.sendMessage(msg)


def unhideAll():
    """show all hidden objects
    """
    msg = "UnhideAll"
    ue4Conn.sendMessage(msg)


def hideByNames(namesList):
    """hide all objects in the namesList
    """
    for name in namesList:
        msg = "HideByName "+name
        ue4Conn.sendMessage(msg)


def unhideByNames(namesList):
    """show all objects in the namesList
    """
    for name in namesList:
        msg = "UnhideByName "+name
        ue4Conn.sendMessage(msg)