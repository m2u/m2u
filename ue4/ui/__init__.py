""" The editor's main UI module.

Provides the integration method for editor-specific UI parts as an addition
into the common UI.

"""

import logging

_lg = logging.getLogger(__name__)


def add_specific_to_common_ui(main_window):
    """ Will be called from within the common PySide UI. Add any editor-
    specific, PySide based UI parts to the main window's layout from here.

    This function must be implemented in the editor-ui-module. If you
    don't have any specific parts to add, leave the body empty.

    """
    # TODO: Getting indices and stuff is maybe a bit weird, an alternative
    #   could be to add specific "addEditorSpecific" functions to the
    #   mainWindow which could then handle the index-positioning internally
    from .ue4PSUIFetchWidget import ue4PSUIFetchWidget
    fetch_widget = ue4PSUIFetchWidget()
    layout = main_window.layout()
    # insert after the Send/Export block
    index = layout.indexOf(main_window.sendGrp)
    # TODO: Add to a specific Get/Import box, not to the general layout
    layout.insertWidget(index + 1, fetch_widget)
