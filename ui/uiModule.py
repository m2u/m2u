"""
m2u main UI module

this is responsible to create a PySide based common UI.

The UI-load-process is initialized by the Program module when requested to generate
the UI by the general initialize script. (program.ui.createUI())

If there is no PySide available, the Program should spawn an internal fallback-UI
by whichever means available to the Program. This module will then never be loaded.

There may exist Program or Editor specific UI parts which can be integrated from
the specific implementations when this module requests them.

It may be necessary for the Program to do some pre-initialization steps to allow a
PySide based UI to run alongside. It may also generally be necessary to attach the
m2u-window to the Programs main window if also Qt based.

"""
import m2u
program = m2u.core.getProgram()

from .m2uMainWindow import m2uMainWindow

uiFolder = m2u.core.getM2uBasePath() + "/ui/"

def createUI(parentQtWindow = None):
    mainWindow = m2uMainWindow(parent = parentQtWindow)
    # now let the program and editor add their specific ui parts
    program.ui.addSpecificToCommonUI(mainWindow)
    


