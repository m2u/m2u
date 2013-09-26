# maya commands, will maybe divided into several files, we will see

import m2u
import pymel.core as pm
#import maya.OpenMaya as mapi
import pymel.api as mapi
import time

RADIAN_TO_DEGR = 57.2957795
DEGR_TO_RADIAN = 0.0174532925

#note: using the following two functions in script jobs would require the full
# path to be specified, since we will eventually move them to udkCommand anyway,
# the functionality is currently inlined into the sj-functions
def rotationMayaToUDK(r):
    # udk has a different rotation order (ZXY), so we transform the stuff here
    global RADIAN_TO_DEGR
    global DEGR_TO_RADIAN
    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    return rx,-ry,-rz

def translationMayaToUDK(t):
    tx,ty,tz = t
    tn = (-tz,tx,ty)
    return tn

def toggleSync( sync ):
    """
    activate or deactivate connection to UDK
    """
    if sync:
        m2u.core.getEditor().connectToInstance() # find ued
        createCameraTracker()
        
    else:
        deleteCameraTracker()


def setCameraFOV( degrees ):
    import pymel.core as pm
    cam = pm.nodetypes.Camera('perspShape',query=True)
    cam.setHorizontalFieldOfView(degrees)


_cameraScriptJob = None
def _onPerspChangedSJ():
    obj = 'persp'
    #tx = pm.getAttr(obj+'.tx')
    #ty = pm.getAttr(obj+'.ty')
    #tz = pm.getAttr(obj+'.tz')
    #rx = pm.getAttr(obj+'.rx')
    #ry = pm.getAttr(obj+'.ry')
    #rz = pm.getAttr(obj+'.rz')
    tx,ty,tz = pm.xform(obj,query=True, ws=True, t=True)
    #tn = translationMayaToUDK((tx,ty,tz)) #script job namespace problem
    tx,ty,tz = (-tz,tx,ty)
    rx,ry,rz = pm.xform(obj,query=True, ws=True, ro=True)
    #rx,ry,rz = rotationMayaToUDK((rx,ry,rz))
    global RADIAN_TO_DEGR
    global DEGR_TO_RADIAN
    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    rx,ry,rz = (rx,-ry,-rz)
    m2u.core.getEditor().setCamera(tx,ty,tz,rx,ry,rz)

def createCameraTracker():
    global _cameraScriptJob
    deleteCameraTracker() # delete if something is amiss so we get a clean new one
    _cameraScriptJob = pm.scriptJob( attributeChange=['persp.inverseMatrix', _onPerspChangedSJ] )

def deleteCameraTracker():
    global _cameraScriptJob
    if  _cameraScriptJob is not None and pm.scriptJob( exists=_cameraScriptJob):
        pm.scriptJob( kill=_cameraScriptJob, force=True)

"""
object tracking works by creating one callback for selection changed tracking
which in turn will create script jobs for all selected objects to survey their transformation values and on a change will execute a sync
all object script jobs will be removed when the selection changed before new SJs are created
"""
_onSelectionChangedCBid = None

def createObjectTracker():
    global _selectionChangedCB
    _onSelectionChangedCBid = mapi.MEventMessage.addEventCallback("SelectionChanged", _onSelectionChangedCB)

def deleteObjectTracker():
    if _onSelectionChangedCB is not None:
        _deleteObjectSJs()
        mapi.MMessage.deleteCallback(_onSelectionChangedCB)

#had to remove the _ prefix or it won't be visible for the script job binding
def onObjectChangedSJ(obj):
    #_objChangedCmd =
    #getting the tx and so won't reflect absolute transformations
    #need to get down to the matrices
    tx,ty,tz = pm.xform(obj,query=True, ws=True, t=True)
    #tx,ty,tz = translationMayaToUDK(t)
    tx,ty,tz = (-tz,tx,ty)
    rx,ry,rz = pm.xform(obj,query=True, ws=True, ro=True)
    #rx,ry,rz = rotationMayaToUDK(r) #script job namespace problem
    global RADIAN_TO_DEGR
    global DEGR_TO_RADIAN
    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    rx,ry,rz = (rx,-ry,-rz)
    sx,sy,sz = pm.xform(obj,query=True, r=True, s=True)
    sx,sy,sz = (sz,sx,sy)
    m2u.core.getEditor().transformObject(obj,(tx,ty,tz),(rx,ry,rz),(sx,sy,sz))

_objectScriptJobs = list()
def _onSelectionChangedCB(data):
    global _objectScriptJobs
    _deleteObjectSJs()
    m2u.core.getEditor().deselectAll()
    time.sleep(0.1)
    for obj in pm.selected():
        #print "obj is "+ obj.name()
        sj = pm.scriptJob( attributeChange=[obj.name()+'.inverseMatrix', "m2u.core.getProgram().onObjectChangedSJ(\""+obj.name()+"\")"] )
        #sj = pm.scriptJob( attributeChange=[obj+'.inverseMatrix', _onObjectChangedCmd"+obj+"] )
        _objectScriptJobs.append(sj)
        m2u.core.getEditor().selectByNames(obj.name())


def _deleteObjectSJs():
    global _objectScriptJobs
    for sj in _objectScriptJobs:
        #print "deleting sj "+str(sj) 
        pm.scriptJob( kill=sj, force=True)
    _objectScriptJobs[:]=[] #empty the list

"""callbacks
playback sync stuff?
MDGMessage.addTimeChangeCallback


duplicated stuff?
import maya.OpenMaya as mapi

def dupCb(data):
    print "dupCb called"
    
mapi.MModelMessage.addAfterDuplicateCallback(dupCb)


mapi.MEventMessage.addEventCallback("NewSceneOpened", ...)
oder SceneOpene: disconnect sync?
alternativ MSceneMessage

"""