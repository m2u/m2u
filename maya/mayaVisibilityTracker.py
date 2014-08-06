""" commands for visibility tracking in maya

Visibility tracking handles hiding, showing and isolating selections and objects.

"""

import pymel.core as pm
import pymel.api as mapi

import m2u

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

import sys
__thismodule = sys.modules[__name__]


############################
# tracking setup functions #
############################

__bVisibilitySync = False
def setVisibilitySyncing( sync ):
    global __bVisibilitySync
    __bVisibilitySync = sync
    if sync:
        createVisibilityTracker()
    else:
        deleteVisibilityTracker()

def isVisibilitySyncing():
    return __bVisibilitySync

# the callback IDs are returned from maya and are used to delete the callbacks
_onCommandExecutedCBid = None

def createVisibilityTracker():
    global _onCommandExecutedCBid
    _onCommandExecutedCBid = mapi.MCommandMessage.addCommandCallback(
        _onCommandExecutedCB)

def deleteVisibilityTracker():
    global _onCommandExecutedCBid
    if _onCommandExecutedCBid is not None:
        mapi.MMessage.removeCallback(_onCommandExecutedCBid)
        _onCommandExecutedCBid = None

# NOTE: for CommandCallback
# Since calling more and more functions with all the same callback string can reduce
# performance significantly, there should only be ONE CommandCallback for all
# of m2u. Wwe should move this callback to some common file and register only the
# functions for specific strings.
def _onCommandExecutedCB(cmd, data):
    if cmd.startswith("hide"):
        _onHide(cmd)
    elif cmd.startswith("showHidden"):
        _onShowHidden(cmd)
    elif cmd.startswith("isolateSelect"):
        _onIsolateSelect(cmd)


def _onHide(cmd):
    """ executed when a 'hide' command was detected """
    # hide all
    if "-all" in cmd:
        #m2u.core.getEditor().hideAll()
        return
    
    # hide list of objects
    listStart = cmd.find("{")
    if listStart > -1: 
        # HACK:
        # We check if the current selection is empty or not.
        # Normally hiding the selected will empty the list, because all visible
        # objects that turn invisible will get deselected.
        # There is the case, where already hidden objects are selected. Those won't
        # be deselected, but they are already invisible, so we can check their
        # visibility flag.
        # If the selection list is empty, hide selected was called.
        # If the selection list contains visible objects, hide unselected was called.
        # If the selection list contains only invisible objects, hide selected.
        # The problem with hiding selected is, that maya deselects the objects
        # before this callback is called, so we have no way of knowing when to disable
        # the syncing. The target Editor will ALWAYS receive the deselect command
        # before we can send the hideSelected command.
        # Thus hideSelected is not possible when syncing selection. To get around this
        # we have to make a collection of objects to hide (they are listed in the
        # cmd string) and tell the Editor to hideByNames
        sl = pm.selected()
        for obj in sl:
            visible = pm.getAttr((obj+".visibility"))
            if visible:
                # hide unselected was called
                m2u.core.getEditor().isolateSelected()
                return
        # selection is empty or contains only invisible objects
        # that means hide selected was called and we have a list to parse
        # the list looks something like this:
        # {"pCube1","pCube2","pCube3","pCube4","pCube5","pCube6","pCube7"};
        listEnd = cmd.find("}")
        cnt = cmd[listStart+2:listEnd-1]
        names = cnt.split('","')
        m2u.core.getEditor().hideByNames(names)
        
    # if no list is provided, it should hide the selected only
    # but this is never executed this way in maya
    else:
        # this most likely never happens in maya!
        m2u.core.getEditor().hideSelected()


def _onShowHidden(cmd):
    """ executed when a 'showHidden' command was detected """
    # show all
    if "-all" in cmd:
        m2u.core.getEditor().unhideAll()
    
    # show list of objects
    elif "{" in cmd:
        #print "SHOWING list of objects DETECTED"
        #TODO: maybe implement this showing of specific objects some day 
        pass
    
    # show selected
    else:
        m2u.core.getEditor().unhideSelected()


def _onIsolateSelect(cmd):
    """ executed when a 'isolateSelect' command was detected """
    # isolate selected
    if " 1 " in cmd:
        m2u.core.getEditor().isolateSelected()
    
    # un-isolate
    elif " 0 " in cmd:
        # TODO: un-isolate is not really unhideAll, it is unhiding all objects
        # that are not really "hidden" in maya, since isolation is done
        # via a viewport set. But we don't really care for now.
        m2u.core.getEditor().unhideAll()