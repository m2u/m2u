""" commands for object tracking in maya

Object tracking works by creating one callback for 'selection changed' tracking
which in turn will create script jobs for all selected objects to survey their
transformation values and on a change will execute a sync.

All object script jobs will be removed when the selection changed before new
SJs are created.

"""

import pymel.core as pm
import pymel.api as mapi

import m2u

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

import sys
__thismodule = sys.modules[__name__]
"""this is required because the script jobs are in mayas namespace,
so absolute paths to functions called inside SJs are required.
Since the path to this module may change, it is easier to get the
real path at runtime instead of hardcoding something.
"""

############################
# tracking setup functions #
############################

__bObjectSync = False
def setObjectSyncing( sync ):
    global __bObjectSync
    __bObjectSync = sync
    if sync:
        createObjectTracker()
    else:
        deleteObjectTracker()

def isObjectSyncing():
    return __bObjectSync


_onSelectionChangedCBid = None
_onBeforeDuplicateCBid = None
_onAfterDuplicateCBid = None
_onNameChangedCBid = None
nullMObject = mapi.OpenMaya.MObject()

def createObjectTracker():
    global _onSelectionChangedCBid
    _onSelectionChangedCBid = mapi.MEventMessage.addEventCallback(
        "SelectionChanged", _onSelectionChangedCB)
    
    global _onBeforeDuplicateCBid, _onAfterDuplicateCBid
    _onBeforeDuplicateCBid = mapi.MModelMessage.addBeforeDuplicateCallback(
        _onBeforeDuplicateCB)
    _onAfterDuplicateCBid = mapi.MModelMessage.addAfterDuplicateCallback(
        _onAfterDuplicateCB)
    
    global _onNameChangedCBid
    _onNameChangedCBid = mapi.MNodeMessage.addNameChangedCallback( nullMObject,
        _onNameChangedCB)

def deleteObjectTracker():
    global _onSelectionChangedCBid
    if _onSelectionChangedCBid is not None:
        _deleteObjectSJs()
        mapi.MEventMessage.removeCallback(_onSelectionChangedCBid)
        _onSelectionChangedCBid = None
    
    global _onAfterDuplicateCBid, _onBeforeDuplicateCBid
    if _onAfterDuplicateCBid is not None:
        mapi.MMessage.removeCallback(_onAfterDuplicateCBid)
        mapi.MMessage.removeCallback(_onBeforeDuplicateCBid)
        _onAfterDuplicateCBid = None
        _onBeforeDuplicateCBid = None
    
    global _onNameChangedCBid
    if _onNameChangedCBid is not None:
        mapi.MMessage.removeCallback(_onNameChangedCBid)
        _onNameChangedCBid = None


#########################
# convenience functions #
#########################

def getTransformationFromObj(obj):
    """ get three float tuples for translate, rotate and scale of the object

    :param obj: the name of the object
    :return: three float tuples for t, r and s
    
    This was initially inside the script job, but it is needed for the
    camera script job and duplicate callback too.

    TODO:
    This function should automatically consider the correct swizzling and
    rotation order conversion for the axis-up-space that is set in maya
    or the UI.

    """
    tx,ty,tz = pm.xform(obj,query=True, ws=True, t=True)
    #tx,ty,tz = translationMayaToUDK(t)
    #tx,ty,tz = (-tz,tx,ty) # y-up
    #tx,ty,tz = (ty,tx,tz) # z-up
    tx,ty,tz = (tx,-ty,tz) # z-up as fbx from udk
    
    rx,ry,rz = pm.xform(obj,query=True, ws=True, ro=True)
    #rx,ry,rz = rotationMayaToUDK(r) #script job namespace problem
    #global RADIAN_TO_DEGR
    #global DEGR_TO_RADIAN

    # maya y-up
#    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
#    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
#    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
#    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
#    rx,ry,rz = (rx,-ry,-rz)

    # maya z-up
    #rx,ry,rz = (rx,-rz,ry) # z-up (same as max)
    rx,ry,rz = (-ry,-rz,rx) # z-up as fbx from udk
    
    sx,sy,sz = pm.xform(obj,query=True, r=True, s=True)
    #sx,sy,sz = (sz,sx,sy) # y-up
    #sx,sy,sz = (sy,sx,sz) # z-up (as max)
    sx,sy,sz = (sx,sy,sz) # z-up as fbx from udk
    
    return ((tx,ty,tz), (rx,ry,rz), (sx,sy,sz))


###########################
# transformation tracking #
###########################

_objectScriptJobs = list()
def _onSelectionChangedCB(data):
    global _objectScriptJobs
    _deleteObjectSJs()
    m2u.core.getEditor().deselectAll()
    for obj in pm.selected():
        # only track transform-nodes
        if obj.nodeType() != "transform":
            continue
        #since the sj is in maya namespace, we need the full qualifier to onObjChanged
        #sj = pm.scriptJob( attributeChange=[obj.name()+'.inverseMatrix',
        #        "m2u.core.getProgram().onObjectChangedSJ(\""+obj.name()+"\")"] )
        sj = pm.scriptJob( attributeChange=[obj.name()+'.inverseMatrix',
                __name__+".onObjectChangedSJ(\""+obj.name()+"\")"] )
        _objectScriptJobs.append(sj)
        m2u.core.getEditor().selectByNames([obj.name()])


def onObjectChangedSJ(obj):
    t,r,s = __thismodule.getTransformationFromObj(obj)
    m2u.core.getEditor().transformObject(obj, t, r, s)
    #m2u.core.getEditor().transformObject(obj,(tx,ty,tz),(rx,ry,rz),(sx,sy,sz))


def _deleteObjectSJs():
    global _objectScriptJobs
    for sj in _objectScriptJobs:
        #print "deleting sj "+str(sj) 
        pm.scriptJob( kill=sj, force=True)
    _objectScriptJobs[:]=[] #empty the list


########################
# duplication tracking #
########################

_beforeDupSelection = None
def _onBeforeDuplicateCB(data):
    """ save the selection to know which objects are going to be duplicated """
    global _beforeDupSelection
    _beforeDupSelection = pm.selected()

def _onAfterDuplicateCB(data):
    """ go through selection (the duplicated objects), get associated original
    object from pre duplicate selection and send the pair to the Editor for
    duplication.

    """
    #print "afterDuplicateCB called"
    afterDupSel = pm.selected()
    if len(afterDupSel) != len(_beforeDupSelection):
        _lg.error(("could not sync duplication, originals and results "
                  "lists are of different lengths"))
        return
    reselectNamesList = list()
    for old, new in zip(_beforeDupSelection, afterDupSel):
        # TODO: check if (old) object exists in udk, if not return early
        t,r,s = getTransformationFromObj(new)
        # now get an unused name from udk
        # if the names mismatch, we need to rename the object in maya
        # the name maya actually assigns to the object may change again
        # so we need to do this until maya and udk use the same name
        mName = str(new) # maya's Name
        uName = "" # Engine's Name
        while True:
            uName = m2u.core.getEditor().getFreeName(mName)
            _lg.debug("Editor returned '"+uName+ "' as a free name.")
            if uName is None: return
            if uName != mName:
                _lg.debug("Name '%s' already in use, need to find a new one." % mName)
                mName = str(pm.rename(mName, uName))
            if uName == mName: # not 'else', because mName may have changed
                break
        result = m2u.core.getEditor().duplicateObject(str(old), uName, t, r, s)
        # TODO: maybe check the return value of duplicateObject call
        # since we changed the name, we need to select the renamed object or
        # the user will get a MayaNodeError when trying to move the duplicates
        # also subsequent duplicates may depend on a correct selection list
        #reselectNamesList.append(mName)
        
        # select waehrend duplicate aufrufen killt den transform wert fuer smart
        # stattdessen muesste entweder ein reselect nach allen duplicates sein
        # ob das geht? oder rename erst nach dem die duplicates erledigt sind
        # duerfte mit dem duplicate callback aber auch problematisch sein
    #pm.select(reselectNamesList, r=True)


########################
# name change tracking #
########################

def _onNameChangedCB(node, prevName, data):
    mfnnode = mapi.MFnDependencyNode(node)
    typeName = mfnnode.typeName()
    if typeName != "transform": # we are not interested in renamed shapes or so
        return
    newName = str(mfnnode.name())
    if "#" in newName: # those are only temporary name changes to create numbers
        return
    if newName.startswith("__"): # temporary duplicate or import names
        return
    _lg.debug("maya changed name to %s" % newName)
    #print "type is %s" % typeName
    m2u.core.getEditor().renameObject(prevName, newName)
    # TODO: handle return code of renameObject appropriately


######################
# deleteion tracking #
######################

def _onDeleteCB(node, data):
    