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

# NOTE: this is currently the only application for a CommandCallback
# Since calling more and more functions with all the same callback string can reduce
# performance significantly, there should only be ONE CommandCallback for all
# of m2u. If there will be more actions requiring a CommandCallback, we should
# move this callback to some common file and register only the functions for specific
# strings.
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
        pass
    
    # hide list of objects
    elif "{" in cmd:
        # we don't parse the whole list of selected objects, that would mean we
        # would have to hide every object "by hand" in the Engine.
        # Instead we check if the first object is found in the current selection list.
        # If it is, the command was "hide selected", if not, it was "hide unselected"
        # TODO: not sure if it works this way, because the selection might change
        # before the callback is executed.
        
        # something like this: hide "-rh" {"pCube1","pCube2","pCube3","pCube4","pCube5","pCube6","pCube7"};
        start = cmd.find("{") + 2 #jump over {"
        end = cmd.find("\"",start)
        name = cmd[start:end]
        
        for obj in pm.selected():
            if obj == name:
                m2u.core.getEditor().hideSelected()
                break
            else:
                m2u.core.getEditor().isolateSelected()
                break
    
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