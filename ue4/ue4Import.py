""" defines functions for commands which interact with UE4

commands will be issued by sending messages to the TCP port through :mod:`ue4Conn`

Import Commands are used for importing Assets from the File System into the Editor.

"""

import os

import m2u
from m2u.ue4 import ue4Conn

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def importAssetsBatch(relFilePathList):
    """
    import all the asset files in the FilePathList
    the files paths have to be relative to the current
    project's ContentRoot.

    This function will create a matching Destination path for each File path.
        
    """
    if len(relFilePathList) < 1:
        return
    
    pipe = m2u.core.getPipeline()
    
    msg = ('ImportAssetsBatch')
    contentRoot = pipe.getProjectExportDir()
    for path in relFilePathList:
        fullpath = contentRoot+"/"+path
        rpath,ext = os.path.splitext(path)
        destination = "/Game/"+rpath.replace("\\","/")
        msg = msg + ' "'+destination+'" "'+fullpath+'"'
    
    result = ue4Conn.sendMessage(msg)