# maya commands, will maybe divided into several files, we will see

#print "maya command importing"

import time
import os

import pymel.core as pm
import pymel.api as mapi

import m2u
import m2u.helper as helper

from m2u import logger as _logger
_lg = _logger.getLogger(__name__)

RADIAN_TO_DEGR = 57.2957795
DEGR_TO_RADIAN = 0.0174532925

#note: using the following two functions in script jobs would require the full
# path to be specified, since we will eventually move them to udkCommand anyway,
# the functionality is currently inlined into the sj-functions
def rotationMayaToUDK(r):
    # udk has a different rotation order (ZXY), so we transform the stuff here
    global RADIAN_TO_DEGR
    global DEGR_TO_RADIAN
    mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN, ry*DEGR_TO_RADIAN,
                               rz*DEGR_TO_RADIAN)
    newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    return rx,-ry,-rz

def translationMayaToUDK(t):
    tx,ty,tz = t
    return -tz,tx,ty #maya y-up
    #return tx,-ty,tz #maya z-up
    #return tx,tz,ty #maya y-up to udk-fbx-z-up?

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

# TODO: move this function to a program-specific pipeline module
# maybe it has to be split in one that is m2u specific and one that
# can be generalized (the importing itself, while still disabling m2u-syncing)
# on the other hand, if somebody provides his own pipeline for m2u, they
# should be able to do this from within those functions too.
def importFile(path):
    """ simply imports an FBX-file
    
    """
    prog = m2u.core.getProgram()
    # disable object tracking, because importing FBX files will cause
    # a lot of renaming and we don't want that to produce warnings
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False)
    
    cmd = "FBXImport -f \""+ path.replace("\\","\\\\") +"\""
    pm.mel.eval(cmd)
    
    prog.setObjectSyncing(wasSyncing) # restore syncing state


#def importAsset()
#def referenceAsset ??

    
# TODO: remove this function or move to UDK specific file
def fetchSelectedObjectsFromEditor():
    """ tell UDK to export the selected objects into a temporary FBX file
    and then maya will import that file.
    
    """
    ed = m2u.core.getEditor()
    prog = m2u.core.getProgram()
    path = m2u.core.getTempFolder()
    path = path + "\m2uTempExport.fbx"
    if os.path.exists(path):
        os.remove(path) # make sure there will be no "overwrite" warning from UEd
    # this is circumventing the interface!
    ed.udkCommand.exportSelectedToFile(path,False)
    status = helper.waitForFileToBecomeAvailable(path)
    if not status:
        _lg.error("Unable to import file: "+path)
        return
    
    # disable object tracking, because importing FBX files will cause
    # a lot of renaming and we don't want that to produce warnings
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False)
    
    cmd = "FBXImport -f \""+ path.replace("\\","\\\\") +"\""
    pm.mel.eval(cmd)
    
    prog.setObjectSyncing(wasSyncing) # restore syncing state


# TODO: move to maya-specific pipeline file
def exportObjectAsAsset(name, path):
    """ export object `name` to FBX file specified by `path`
    and edit/add the `MeshPath` attribute accordingly.

    if a `MeshPath` attribute is found and is not empty,
    that name will be presented to the user n shit
    then the user can decide how to change the name (the signature)
    the path will actually be created from the signature, based on the
    project base directory that should be specified in the "pipeline"
    settings of m2u, if nothing is set there, the TEMP folder should be used
    then may check the already existing files in the directory and increase
    a suffix on the meshname to create a unique new one, and present that to
    the user?

    """
    pm.addAttr(longName="MeshPath", dataType="string", keyable=False)
    obj=pm.selected()[0]
    attr = pm.getAttr(obj.name()+".MeshPath")
    print attr

# TODO: move to maya-specific pipeline-file
def exportObjectCentered(name, path, center=True):
    """ export object `name` to FBX file specified by `path`
    
    :param name: objects name
    :param path: file path for the fbx file
    :param center: object transformation will be reset before export

    """
    prog = m2u.core.getProgram()
    wasSyncing = prog.isObjectSyncing()
    prog.setObjectSyncing(False) # so our move command won't be reflected in Ed
    
    pm.select(name, r=True)
    mat = pm.xform(query=True, ws=True, m=True) # backup matrix
    if center:
        pm.xform(a=True, ws=True, t=(0,0,0), ro=(0,0,0), s=(1,1,1))
    
    exportSelectedToFBX(path)
    
    if center:
        pm.xform( a=True, ws=True, m=mat) # reset matrix
    
    prog.setObjectSyncing(wasSyncing) # restore syncing state
        

# TODO: move to maya-specific pipeline-file
def exportSelectedToFBX(path):
    """ export selection to file specified by `path`

    fbx settings will be set from `fbxSettings` preset file
    """
    if os.path.exists(path):
        os.remove(path) 
    sfpath = m2u.core.getM2uBasePath()+"/fbxExportPreset.cfg"
    lsfcmd = "FBXLoadExportPresetFile -f %s"
    expcmd = "FBXExport -f \"%s\" -s" % path.replace("\\","\\\\")



def printWarning(s):
    pm.warning(s)










