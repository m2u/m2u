# maya commands, will maybe divided into several files, we will see

import m2u
import pymel.core as pm

def setViewFOF( degrees ):
    pass

def toggleSync( sync ):
    """
    activate or deactivate connection to UDK
    """
    if sync:
        m2u.getEditor().connectToInstance() # find ued
        createCameraTracker()
        
    else:
        deleteCameraTracker()

cameraScriptJob = None
def perspChanged():
    tx = pm.getAttr('persp.tx')
    ty = pm.getAttr('persp.ty')
    tz = pm.getAttr('persp.tz')
    rx = pm.getAttr('persp.rx')
    ry = pm.getAttr('persp.ry')
    rz = pm.getAttr('persp.rz')
    m2u.getEditor().setCamera(-tz,tx,ty,rx,-ry,rz)

def createCameraTracker():
    global cameraScriptJob
    pm.scriptJob( attributeChange=['persp.inverseMatrix', perspChanged] )

def deleteCameraTracker():
    global cameraScriptJob
    pm.scriptJob( kill=cameraScriptJob, force=True)