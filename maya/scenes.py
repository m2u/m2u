"""Commands for scene events tracking in maya.

Scene tracking observes if files are opened, closed or Maya exits.
That may be important for deleting and recreating callbacks automatically.

When Maya exits, we will try to disconnect from the Editor and save
settings.

"""

import logging

import pymel.api as mapi

import m2u

_lg = logging.getLogger(__name__)


def create_maya_exit_tracker():
    mapi.MSceneMessage.addCallback(mapi.MSceneMessage.kMayaExiting,
                                   _on_maya_exiting)


def _on_maya_exiting(data):
    m2u.core.editor.disconnect()
    m2u.core.settings.save_config()


# Register the exit-tracker when loading this module:
create_maya_exit_tracker()
