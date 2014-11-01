"""
the programs main UI module
will try to initialize creation of the common PySide based UI if possible.

If PySide can not be loaded create a fallback-UI.

Also provides the integration method for program-specific UI parts as an addition
into the common UI.

"""

import m2u
from m2u import logger as _logger
_lg = _logger.getLogger(__name__)


def createUI():
    """create the PySide based UI or a fallback if necessary.
    """
    # (we try to dynamically load PySide here because this module is initialized)
    # (before the Editor module is loaded, but both must exist before UI-creation.)
    # If loading of PySide fails, the fallback will be created.
    loadCommonUI = True
    try:
        import PySide
    except ImportError:
        _lg.error("Unable to load PySide, trying to create a fallback-UI.")
        loadCommonUI = False
        
    if not loadCommonUI:
        from m2u.maya import mayaInternalUI
        mayaInternalUI.createUI()
    else:
        from m2u import ui
        from maya import OpenMayaUI as omui
        from PySide import QtGui
        from shiboken import wrapInstance
        
        mayaMainWindowPtr = omui.MQtUtil.mainWindow() 
        mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget) 
        ui.createUI(mayaMainWindow)
