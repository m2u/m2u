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

import sys
__thismodule = sys.modules[__name__]
"""this is required because the script jobs are in mayas namespace,
so absolute paths to functions called inside SJs are required.
Since the path to this module may change, it is easier to get the
real path at runtime instead of hardcoding something.
"""

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

def createObjectTracker():
    global _onSelectionChangedCBid
    _onSelectionChangedCBid = mapi.MEventMessage.addEventCallback(
        "SelectionChanged", _onSelectionChangedCB)

def deleteObjectTracker():
    global _onSelectionChangedCBid
    if _onSelectionChangedCBid is not None:
        _deleteObjectSJs()
        mapi.MEventMessage.removeCallback(_onSelectionChangedCBid)
        _onSelectionChangedCBid = None

def getTransformationFromObj(obj):
    """ get three float tuples for translate, rotate and scale of the object

    :param obj: the name of the object
    :return: three float tuples for t, r and s
    
    This was initially inside the script job, but it is needed for the
    camera script job too.

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

def onObjectChangedSJ(obj):
    t,r,s = __thismodule.getTransformationFromObj(obj)
    m2u.core.getEditor().transformObject(obj, t, r, s)
    #m2u.core.getEditor().transformObject(obj,(tx,ty,tz),(rx,ry,rz),(sx,sy,sz))

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


def _deleteObjectSJs():
    global _objectScriptJobs
    for sj in _objectScriptJobs:
        #print "deleting sj "+str(sj) 
        pm.scriptJob( kill=sj, force=True)
    _objectScriptJobs[:]=[] #empty the list
