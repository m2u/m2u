""" commands for the maya camera """


import pymel.core as pm
import m2u
#import m2u.maya.mayaObjectTracker as mObj
from m2u.maya import mayaObjectTracker as mObj

import sys
__thismodule = sys.modules[__name__]

__bCameraSync = False
def setCameraSyncing( sync ):
    global __bCameraSync
    __bCameraSync = sync
    if sync:
        createCameraTracker()
    else:
        deleteCameraTracker()

def isCameraSyncing():
    return __bCameraSync

def setCameraFOV( degrees ):
    cam = pm.nodetypes.Camera('perspShape',query=True)
    cam.setHorizontalFieldOfView(degrees)

def setupCamera():
    """ set position, clip planes and fov of default cameras to work better
    with the bigger size of udk scenes.
    """
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
    t,r,s = __thismodule.mObj.getTransformationFromObj(obj)
    rx,ry,rz = pm.xform(obj,query=True, ws=True, ro=True)
    r = (rx-90,-rz-90,ry) # z-up as fbx from udk?
    m2u.core.getEditor().transformCamera(t[0],t[1],t[2],r[0],r[1],r[2])
    
def createCameraTracker():
    global _cameraScriptJob
    deleteCameraTracker() # delete if something is amiss so we get a clean new one
    _cameraScriptJob = pm.scriptJob( attributeChange=['persp.inverseMatrix',
                                                      _onPerspChangedSJ] )

def deleteCameraTracker():
    global _cameraScriptJob
    if  _cameraScriptJob is not None and pm.scriptJob( exists=_cameraScriptJob):
        pm.scriptJob( kill=_cameraScriptJob, force=True)
        _cameraScriptJob = None

