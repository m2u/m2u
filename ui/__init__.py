""" m2u main UI module

This is responsible to create a PySide based common UI.

The UI-load-process is initialized by the Program module when requested
to generate the UI by the general initialize script
`program.ui.create_ui()`

There may exist Program or Editor specific UI parts which can be
integrated from the specific implementations when this module requests
them.

It may be necessary for the Program to do some pre-initialization steps
to allow a PySide based UI to run alongside. It may also generally be
necessary to attach the m2u-window to the Programs main window.

"""

import sys
import logging

from PySide import QtGui

from m2u import core

this = sys.modules[__name__]

_lg = logging.getLogger(__name__)


this.main_window = None
this.window_base_class = QtGui.QWidget


def set_window_base_class(cls):
    """Only takes effect when called before create_ui."""
    this.window_base_class = cls


def create_ui(parent_window):
    from .mainwindow import MainWindow
    if this.main_window is None:
        _lg.info("No m2u window found, creating a new one.")
        this.main_window = MainWindow()
        # Now let the Program and Editor add their specific ui parts.
        core.program.ui.add_specific_to_common_ui(this.main_window)
        core.editor.ui.add_specific_to_common_ui(this.main_window)
    this.main_window.show()
