""" The program's main UI module.
"""

import logging

_lg = logging.getLogger(__name__)


def create_ui():
    """ Create the PySide based UI.
    """
    # Note: We try to dynamically load PySide here because this module
    #   is initialized before the Editor module is loaded, but both must
    #   exist before UI-creation.
    try:
        # The import is only to determine if PySide exists.
        import PySide  # noqa
    except ImportError:
        _lg.error("Unable to load PySide.")
        raise

    from m2u import ui
    from maya import OpenMayaUI as omui
    from PySide import QtGui
    from shiboken import wrapInstance

    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    maya_main_window = wrapInstance(long(maya_main_window_ptr), QtGui.QWidget)
    # from maya.app.general import mayaMixin
    # mayaQtBaseClass = mayaMixin.MayaQWidgetDockableMixin
    # mayaQtBaseClass = mayaMixin.MayaQWidgetBaseMixin
    # ui.set_window_base_class(mayaQtBaseClass)
    ui.create_ui(maya_main_window)


def add_specific_to_common_ui(main_window):
    """ Will be called from within the common PySide UI. Add any program-
    specific PySide based UI parts to the main window's layout from here.

    This function must be implemented in the program-ui-module. If you
    don't have any specific parts to add, leave the body empty.

    """
    from .mayaPSUICameraWidget import mayaPSUICameraWidget
    camera_widget = mayaPSUICameraWidget()
    layout = main_window.layout()
    # insert after the connect-line
    index = layout.indexOf(main_window.topRowWidget)
    layout.insertWidget(index+1, camera_widget)
