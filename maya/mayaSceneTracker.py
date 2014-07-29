""" commands for scene events tracking in maya

Scene tracking observes if files are opened, closed or Maya exits.
That may be important for deleting and recreating callbacks automatically.

When Maya exits, we will try to disconnect from the Editor and save settings.

"""

import pymel.core as pm
import pymel.api as mapi

import m2u

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

import sys
__thismodule = sys.modules[__name__]


def createMayaExitTracker():
    mapi.MSceneMessage.addCallback(mapi.MSceneMessage.kMayaExiting, _onMayaExiting)

def _onMayaExiting(data):
    m2u.core.getEditor().disconnect()
    m2u.core.settings.saveConfig()

# auto crete the ExitTracker when loading this module:
createMayaExitTracker()