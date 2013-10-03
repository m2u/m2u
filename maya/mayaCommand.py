# maya commands, will maybe divided into several files, we will see

import m2u
import m2u.helper as helper
import pymel.core as pm
#import maya.OpenMaya as mapi
import pymel.api as mapi
import time
import os

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
    return -tz,tx,ty #maya y-up
    #return tx,-ty,tz #maya z-up

__bCameraSync = False
def setCameraSyncing( sync ):
    global __bCameraSync
    __bCameraSync = sync
    if sync:
        createCameraTracker()
    else:
        deleteCameraTracker()

def isCameraSyncing():
    #global __bCameraSync
    return __bCameraSync

__bObjectSync = False
def setObjectSyncing( sync ):
    global __bObjectSync
    __bObjectSync = sync
    if sync:
        createObjectTracker()
    else:
        deleteObjectTracker()

def isObjectSyncing():
    #global __bObjectSync
    return __bObjectSync

#def toggleSync( sync ):
#    """
#    activate or deactivate connection to UDK
    # """
    # if sync:
    #     m2u.core.getEditor().connectToInstance() # find ued
    #     createCameraTracker()
        
    # else:
    #     deleteCameraTracker()


def setCameraFOV( degrees ):
    cam = pm.nodetypes.Camera('perspShape',query=True)
    cam.setHorizontalFieldOfView(degrees)

def setupCamera():
    cam = pm.nodetypes.Camera('perspShape',query=True)
    cam.setFarClipPlane(65536.0)
    cam.setNearClipPlane(10.0)
    setCameraFOV(90.0)
    cam = pm.nodetypes.Camera('topShape',query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('top.ty',50000.0)
    cam = pm.nodetypes.Camera('frontShape',query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('front.tz',50000.0)
    cam = pm.nodetypes.Camera('sideShape',query=True)
    cam.setFarClipPlane(100000.0)
    cam.setNearClipPlane(10.0)
    pm.setAttr('side.tx',50000.0)

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
    #tx,ty,tz = (-tz,tx,ty) # y-up
    #tx,ty,tz = (ty,tx,tz) # z-up (same as max)
    tx,ty,tz = (tx,-ty,tz) # z-up as fbx from udk?
    
    rx,ry,rz = pm.xform(obj,query=True, ws=True, ro=True)
    #rx,ry,rz = rotationMayaToUDK((rx,ry,rz))
    #global RADIAN_TO_DEGR
    #global DEGR_TO_RADIAN
    
    # maya y-up    
#    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
#    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
#    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
#    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
#    rx,ry,rz = (rx,-ry,-rz) # y-up
    
    # maya z-up
    #rx,ry,rz = (rx-90,-rz,ry) # z-up (same as max)
    rx,ry,rz = (rx-90,-rz-90,ry) # z-up as fbx from udk?
    m2u.core.getEditor().setCamera(tx,ty,tz,rx,ry,rz)

def createCameraTracker():
    global _cameraScriptJob
    deleteCameraTracker() # delete if something is amiss so we get a clean new one
    _cameraScriptJob = pm.scriptJob( attributeChange=['persp.inverseMatrix', _onPerspChangedSJ] )

def deleteCameraTracker():
    global _cameraScriptJob
    if  _cameraScriptJob is not None and pm.scriptJob( exists=_cameraScriptJob):
        pm.scriptJob( kill=_cameraScriptJob, force=True)
        _cameraScriptJob = None

"""
object tracking works by creating one callback for selection changed tracking
which in turn will create script jobs for all selected objects to survey their transformation values and on a change will execute a sync
all object script jobs will be removed when the selection changed before new SJs are created
"""
_onSelectionChangedCBid = None

def createObjectTracker():
    global _onSelectionChangedCBid
    _onSelectionChangedCBid = mapi.MEventMessage.addEventCallback("SelectionChanged", _onSelectionChangedCB)

def deleteObjectTracker():
    global _onSelectionChangedCBid
    if _onSelectionChangedCBid is not None:
        _deleteObjectSJs()
        mapi.MEventMessage.removeCallback(_onSelectionChangedCBid)
        _onSelectionChangedCBid = None

#had to remove the _ prefix or it won't be visible for the script job binding
def onObjectChangedSJ(obj):
    #_objChangedCmd =
    #getting the tx and so won't reflect absolute transformations
    #need to get down to the matrices
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
    m2u.core.getEditor().transformObject(obj,(tx,ty,tz),(rx,ry,rz),(sx,sy,sz))

_objectScriptJobs = list()
def _onSelectionChangedCB(data):
    global _objectScriptJobs
    _deleteObjectSJs()
    m2u.core.getEditor().deselectAll()
    #time.sleep(0.1)
    for obj in pm.selected():
        #print "obj is "+ obj.name()
        # only track transform-nodes
        if obj.nodeType() != "transform":
            continue
        #since the sj is in maya namespace, we need the full qualifier to onObjChanged
        sj = pm.scriptJob( attributeChange=[obj.name()+'.inverseMatrix', "m2u.core.getProgram().onObjectChangedSJ(\""+obj.name()+"\")"] )
        #sj = pm.scriptJob( attributeChange=[obj+'.inverseMatrix', _onObjectChangedCmd"+obj+"] )
        _objectScriptJobs.append(sj)
        m2u.core.getEditor().selectByNames([obj.name()])


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

def fetchSelectedObjectsFromEditor():
    """ this function will tell UDK to export the selected objects into a temporary FBX file and then maya will import that file"""
    #path = os.getenv("TEMP")
    path = m2u.core.getTempFolder()
    path = path + "\m2uTempExport.fbx"
    if os.path.exists(path):
        os.remove(path) # make sure there will be no "overwrite" warning from UEd
    m2u.core.getEditor().exportSelectedToFile(path,False)
    #while not os.path.exists(path):
    #    time.sleep(0.01) # wait till file is being written
    #    #print "waited a little"
    #time.sleep(0.1) # wait a little longer, hope file is finished written
    #TODO: find some way to check if the file is still being written or not
    #print "# m2u: Importing file: "+path
    status = helper.waitForFileToBecomeAvailable(path)
    if not status:
        pm.error("# m2u: Unable to import file: "+path)
        return
    
    cmd = "FBXImport -f \""+ path.replace("\\","\\\\") +"\""
    pm.mel.eval(cmd)