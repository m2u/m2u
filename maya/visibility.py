""" Commands for visibility tracking in maya.

Visibility tracking handles hiding, showing and isolating selections
and objects.

"""

import sys
import logging

import pymel.core as pm
import pymel.api as mapi

import m2u

_lg = logging.getLogger(__name__)

this = sys.modules[__name__]

this._is_visibility_syncing = False

# The callback IDs are returned from maya and are used to delete the callbacks.
this._on_command_executed_cb_id = None


def set_visibility_syncing(sync):
    this._is_visibility_syncing = sync
    if sync:
        _create_visibility_tracker()
    else:
        _delete_visibility_tracker()


def is_visibility_syncing():
    return this._is_visibility_syncing


def _create_visibility_tracker():
    this._on_command_executed_cb_id = mapi.MCommandMessage.addCommandCallback(
        _on_command_executed_cb)


def _delete_visibility_tracker():
    if this._on_command_executed_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_command_executed_cb_id)
        this._on_command_executed_cb_id = None


def _on_command_executed_cb(cmd, data):
    if cmd.startswith("hide"):
        _on_hide(cmd)
    elif cmd.startswith("showHidden"):
        _on_show_hidden(cmd)
    elif cmd.startswith("isolateSelect"):
        _on_isolate_select(cmd)


def _on_hide(cmd):
    """ Executed when a 'hide' command was detected. """
    # hide all
    if "-all" in cmd:
        # TODO: Why is this disabled?
        # m2u.core.editor.hide_all()
        return

    # hide list of objects
    list_start = cmd.find("{")
    if list_start > -1:
        # HACK: We check if the current selection is empty or not.
        #   Normally hiding the selected will empty the list, because
        #   all visible objects that turn invisible will get deselected.
        #   There is the case, where already hidden objects are selected.
        #   Those won't be deselected, but they are already invisible,
        #   so we can check their visibility flag.
        #
        #   If the selection list is empty, hide selected was called.
        #   If the selection list contains visible objects, hide
        #   unselected was called.
        #   If the selection list contains only invisible objects, hide
        #   selected was called.
        #
        #   The problem with hiding selected is, that maya deselects the
        #   objects before this callback is called, so we have no way of
        #   knowing when to disable the syncing.
        #   The target Editor will ALWAYS receive the deselect command
        #   before we can send the hideSelected command.
        #   Thus hideSelected is not possible when syncing selection.
        #   To get around this, we have to make a collection of objects
        #   to hide (they are listed in the cmd string) and tell the
        #   Editor to hide by a list of names.
        sl = pm.selected()
        for obj in sl:
            visible = pm.getAttr(obj+".visibility")
            if visible:
                # hide unselected was called
                m2u.core.editor.isolate_selected()
                return
        # Selection is empty or contains only invisible objects. That
        # means hide selected was called and we have a list to parse.
        # The list (string) looks something like this:
        # {"pCube1","pCube2","pCube3","pCube4","pCube5","pCube6","pCube7"};
        list_end = cmd.find("}")
        content = cmd[list_start + 2: list_end - 1]
        names = content.split('","')
        m2u.core.editor.hide_by_names(names)

    else:
        # If no list is provided, it should hide the selected only, but
        # this seems to never be executed this way in maya.
        m2u.core.editor.hide_selected()


def _on_show_hidden(cmd):
    """ Executed when a 'showHidden' command was detected. """
    # show all
    if "-all" in cmd:
        m2u.core.editor.unhide_all()

    # show list of objects
    elif "{" in cmd:
        # TODO: Consider implementation of showing of specified objects.
        _lg.warning("Not Implemented: SHOWING list of objects.")

    # show selected
    else:
        m2u.core.editor.unhide_selected()


def _on_isolate_select(cmd):
    """ Executed when an 'isolateSelect' command was detected. """
    # isolate selected
    if " 1 " in cmd:
        m2u.core.editor.isolate_selected()

    # un-isolate
    elif " 0 " in cmd:
        # TODO: un-isolate is not really unhideAll, it is unhiding all
        #   objects that are not really "hidden" in maya, since isolation
        #   is done via a viewport set.
        #   We need to get the list of objects from the viewport set or
        #   so, if that is still available when this command is received.
        m2u.core.editor.unhide_all()
