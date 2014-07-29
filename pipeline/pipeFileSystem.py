"""
m2u minimal pipeline

Tasks that operate on the File-System like creating, deleting, checking files
and folders.

"""

import os
import tempfile

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)
import m2u.settings as settings


def getTempFolder():
    """ get the Tempdir path from the settings or use the os-default
    if not set in settings file

    """
    tmpdir = tempfile.gettempdir()
    p = settings.getAndSetValueDefaultIfError("General","Tempdir",
                                              tmpdir, False)
    return p


def getProjectExportDir():
    """ get the base directory for content of the current user's project
    folder. Used when exporting and importing mesh-files.

    """
    # TODO: this is a pipeline task and should be moved to a new file
    # for common pipeline functionality
    return getTempFolder()+"/m2u_Export"