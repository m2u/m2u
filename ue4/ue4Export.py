""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

Export Commands are used for exporting Assets from the Editor to the File System.

"""

import m2u
from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def fetchSelectedObjects():
    """ fast-fetch all selected actors by exporting them into an FBX-File and
    importing that file into the Program.
    Only one file containing all Objects is created.
    This should not be used for creating reusable assets!

    """
    ed = m2u.core.getEditor()
    prog = m2u.core.getProgram()
    pipe = m2u.core.getPipeline()
    
    path = pipe.getTempFolder()
    path = path + "\m2uTempExport.fbx"
    
    msg = ("FetchSelected \""+path+"\"")
    result = ue4Conn.sendMessage(msg)
    prog.importFile(path)