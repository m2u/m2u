"""
the editor's main UI module

Provides the integration method for editor-specific UI parts as an addition
into the common UI.

"""

import m2u
from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

def addSpecificToCommonUI(mainWindow):
    """ will be called from within the common PySide UI. Add any editor-specific
    PySide based UI parts to the main window's layout from here.

    This function must be implemented in the editor-ui-module. If you don't have
    any specific parts to add, leave the body empty.
    
    """
    # TODO: getting indices and stuff is maybe a bit weird, an alternative
    # could be to add specific "addEditorSpecific" functions to the mainWindow
    # which could then handle the index-positioning internally
    from .ue4PSUIFetchWidget import ue4PSUIFetchWidget
    fetchWidget = ue4PSUIFetchWidget()
    layout = mainWindow.layout()
    # insert after the Send/Export block
    index = layout.indexOf(mainWindow.sendGrp)
    # TODO: add to a Get/Import box not to the general layout
    layout.insertWidget( index+1, fetchWidget )