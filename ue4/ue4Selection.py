""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

"""

from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def selectByNames(namesList):
    """add objects to the current selection

    :param namesList: list containing the object names

    """
    names = "["+(','.join(namesList))+"]"
    msg = ("SelectByNames "+names)
    ue4Conn.sendMessage(msg)


def deselectAll():
    """clear the current selection
    """
    ue4Conn.sendMessage("DeselectAll")

def deselectByNames(namesList):
    """remove objects from the current selection
    
    :param namesList: list containing the object names

    """
    names = "["+(','.join(namesList))+"]"
    msg = ("DeselectByNames "+names)
    ue4Conn.sendMessage(msg)