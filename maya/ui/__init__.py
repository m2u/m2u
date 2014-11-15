"""
the program's main UI module
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


def addSpecificToCommonUI(mainWindow):
    """ will be called from within the common PySide UI. Add any program-specific
    PySide based UI parts to the main window's layout from here.

    This function must be implemented in the program-ui-module. If you don't have
    any specific parts to add, leave the body empty.
    
    """
    from .mayaPSUICameraWidget import mayaPSUICameraWidget
    cameraWidget = mayaPSUICameraWidget()
    layout = mainWindow.layout()
    # insert after the connect-line
    layout.insertWidget(1,cameraWidget)

