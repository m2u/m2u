""" commands for object tracking in maya

Object tracking works by creating one callback for 'selection changed' tracking
which in turn will create script jobs for all selected objects to survey their
transformation values and on a change will execute a sync.

All object script jobs will be removed when the selection changed before new
SJs are created.

Other callbacks are created to track if objects are created, deleted, renamed, 
parent-child relationships change, 

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


# the callback IDs are returned from maya and are used to delete the callbacks
_onSelectionChangedCBid = None
_onBeforeDuplicateCBid = None
_onAfterDuplicateCBid = None
_onNameChangedCBid = None
_onObjectCreatedCBid = None
_onObjectDeletedCBid = None
_onParentChangedCBid=None

def getObjectSyncingState():
    """ which object trackers are active
    returns a dictionary with name:bool pairs that can be fed back into the
    func:`setObjectSyncingState()` function.
    """
    states = { "selection" : False if _onSelectionChangedCBid is None else True,
               "duplicate" : False if _onBeforeDuplicateCBid is None else True,
               "name" : False if _onNameChangedCBid is None else True,
               "existence" : False if _onObjectDeletedCBid is None else True,
               "relationship" : False if _onParentChangedCBid is None else True
    }
    return states


def setObjectSyncingState(**kwargs):
    """ activate or disable specific trackers
    """
    if "selection" in kwargs.keys():
        createSelectionTracker() if kwargs["selection"] else deleteSelectionTracker()
    if "duplicate" in kwargs.keys():
        createDuplicateTracker() if kwargs["duplicate"] else deleteDuplicateTracker()
    if "name" in kwargs.keys():
        createNameTracker() if kwargs["name"] else deleteNameTracker()
    if "existence" in kwargs.keys():
        createExistenceTracker() if kwargs["existence"] else deleteExistenceTracker()
    if "relationship" in kwargs.keys():
        (createRelationshipTracker() if kwargs["relationship"]
         else deleteRelationshipTracker())


# some callback functions expect a specific node to create a callback for
# passing a nullMObject makes some of those functions track all nodes instead
nullMObject = mapi.OpenMaya.MObject()

def createObjectTracker():
    """ create all callbacks that track object-changes
    """
    createSelectionTracker()
    createDuplicateTracker()
    createNameTracker()
    createExistenceTracker()
    createRelationshipTracker()

def deleteObjectTracker():
    """ delete all callbacks that track object-changes
    """
    deleteSelectionTracker()
    deleteDuplicateTracker()
    deleteNameTracker()
    deleteExistenceTracker()
    deleteRelationshipTracker()


# these functions always delete old trackers before creating the new ones
# just to make sure there aren't suddenly two callbacks doing the same
# the alternative would be to check if the callbacks are None, but we suppose
# we really want to create NEW callbacks for some reason, when calling these funcs
def createSelectionTracker():
    deleteSelectionTracker() 
    global _onSelectionChangedCBid
    _onSelectionChangedCBid = mapi.MEventMessage.addEventCallback(
        "SelectionChanged", _onSelectionChangedCB)
    # automatically create tracking script jobs on the current selection
    # but don't emit "selection changed" or it will be emitted very often during
    # tracking-disabling operations like duplication and name-changing
    #_onSelectionChangedCB(None)
    _createObjectScriptJobsNoSelChanged()

def createDuplicateTracker():
    deleteDuplicateTracker()
    global _onBeforeDuplicateCBid, _onAfterDuplicateCBid
    _onBeforeDuplicateCBid = mapi.MModelMessage.addBeforeDuplicateCallback(
        _onBeforeDuplicateCB)
    _onAfterDuplicateCBid = mapi.MModelMessage.addAfterDuplicateCallback(
        _onAfterDuplicateCB)

def createNameTracker():
    deleteNameTracker()
    global _onNameChangedCBid
    _onNameChangedCBid = mapi.MNodeMessage.addNameChangedCallback( nullMObject,
        _onNameChangedCB)

def createExistenceTracker():
    deleteExistenceTracker()
    global _onObjectCreatedCBid, _onObjectDeletedCBid
    nodeType = "transform" # TODO: maybe use "dagObject" and filter afterwards
    #_onObjectCreatedCBid = mapi.MDGMessage.addNodeAddedCallback(
    #    _onObjectCreatedCB, nodeType)
    _onObjectDeletedCBid = mapi.MDGMessage.addNodeRemovedCallback(
        _onObjectDeletedCB, nodeType)

def createRelationshipTracker():
    deleteRelationshipTracker()
    global _onParentChangedCBid
    #_onParentChangedCBid = mapi.MDagMessage.addAllDagChangesCallback(
    _onParentChangedCBid = mapi.MDagMessage.addParentAddedCallback(
        _onParentChangedCB)


def deleteSelectionTracker():
    global _onSelectionChangedCBid
    if _onSelectionChangedCBid is not None:
        _deleteObjectSJs()
        mapi.MEventMessage.removeCallback(_onSelectionChangedCBid)
        _onSelectionChangedCBid = None

def deleteDuplicateTracker():
    global _onAfterDuplicateCBid, _onBeforeDuplicateCBid
    if _onAfterDuplicateCBid is not None:
        mapi.MMessage.removeCallback(_onAfterDuplicateCBid)
        mapi.MMessage.removeCallback(_onBeforeDuplicateCBid)
        _onAfterDuplicateCBid = None
        _onBeforeDuplicateCBid = None

def deleteNameTracker():
    global _onNameChangedCBid
    if _onNameChangedCBid is not None:
        mapi.MMessage.removeCallback(_onNameChangedCBid)
        _onNameChangedCBid = None

def deleteExistenceTracker():
    global _onObjectCreatedCBid, _onObjectDeletedCBid
    if _onObjectCreatedCBid is not None:
        mapi.MMessage.removeCallback(_onObjectCreatedCBid)
        _onObjectCreatedCBid = None
    if _onObjectDeletedCBid is not None:
        mapi.MMessage.removeCallback(_onObjectDeletedCBid)
        _onObjectDeletedCBid = None

def deleteRelationshipTracker():
    global _onParentChangedCBid
    if _onParentChangedCBid is not None:
        mapi.MMessage.removeCallback(_onParentChangedCBid)
        _onParentChangedCBid = None



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

    TODO:
    currently conversion from maya to UDK/UE4 space is hard coded here.
    This will not work for Unity and the like. This functionality has to
    be reworked.

    """
    # if the engine supports nested transforms, world-space transforms
    # will mess up the result
    useWorldSpace = not m2u.core.getEditor().supportsParenting()
    
    # the translate values in the matrix will always reflect the TRUE translation
    # while parenting and pivots mess up the the other results
    mat = pm.xform(obj, query=True, m = True, ws = useWorldSpace )
    #tx,ty,tz = pm.xform(obj,query=True, ws=useWorldSpace, t=True)
    tx, ty, tz = (mat[12],mat[13],mat[14])
    #tx,ty,tz = translationMayaToUDK(t)
    #tx,ty,tz = (-tz,tx,ty) # y-up
    #tx,ty,tz = (ty,tx,tz) # z-up
    tx,ty,tz = (tx,-ty,tz) # z-up as fbx from udk
    
    rx,ry,rz = pm.xform(obj,query=True, ws=useWorldSpace, ro=True)
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
    """ create the object tracking script jobs and tell the editor to update the
    selection.
    """
    m2u.core.getEditor().deselectAll()
    _createObjectScriptJobsNoSelChanged()
    for obj in pm.selected():
        m2u.core.getEditor().selectByNames([obj.name()])


def _createObjectScriptJobsNoSelChanged():
    """ create the object tracking script jobs without emitting a selection changed
    to the editor
    """
    global _objectScriptJobs
    _deleteObjectSJs()
    
    # If we can NOT use parenting, we need to make sure all the objects
    # that are children of the selected objects in maya are explicitly synced
    # if parenting is possible, the transforms will be implicitly synced because
    # they are relative to the parent in the Engine anyway.

    completeObjList = pm.selected()
    if not m2u.core.getEditor().supportsParenting():
        for obj in pm.selected():
            children = pm.listRelatives(obj, allDescendents = True,
                                        noIntermediate = True, type="transform")
            completeObjList.extend(children)
            
    print "completeObjList: "+str(completeObjList)
    completeObjSet = set(completeObjList)
    print "completeObjSet: "+str(completeObjSet)
    for obj in completeObjSet:
        # only track transform-nodes
        if obj.nodeType() != "transform":
            continue
        #since the sj is in maya namespace, we need the full qualifier to onObjChanged
        sj = pm.scriptJob( attributeChange=[obj.name()+'.rotatePivot',
                __name__+".onObjectChangedSJ(\""+obj.name()+"\")"] )
        _objectScriptJobs.append(sj)
        #sj = pm.scriptJob( attributeChange=[obj.name()+'.parentMatrix',
        #        __name__+".onObjectChangedSJ(\""+obj.name()+"\")"] )
        #_objectScriptJobs.append(sj)


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
_beforeDupSyncState = None
def _onBeforeDuplicateCB(data):
    """ save the selection to know which objects are going to be duplicated """
    global _beforeDupSelection
    _beforeDupSelection = pm.selected()
    # we have to disable rename and parent tracking, so we don't try
    # to make stuff with intermediate objects
    global _beforeDupSyncState
    _beforeDupSyncState = getObjectSyncingState()
    setObjectSyncingState(name = False, selection = False, relationship = False)


def _onAfterDuplicateCB(data):
    """ go through selection (the duplicated objects), get associated original
    object from pre duplicate selection and send the pair to the Editor for
    duplication.

    """
    afterDupSel = pm.selected()
    if len(afterDupSel) != len(_beforeDupSelection):
        _lg.error(("could not sync duplication, originals and results "
                  "lists are of different lengths"))
        return
    reselectNamesList = list()
    for old, new in zip(_beforeDupSelection, afterDupSel):
        # TODO: check if (old) object exists in udk, if not return early
        t,r,s = getTransformationFromObj(new)
        # now get an unused name from the editor
        # if the names mismatch, we need to rename the object in maya
        # the name maya actually assigns to the object may change again
        # so we need to do this until maya and the editor use the same name
        mName = str(new) # maya's Name
        uName = "" # Engine's Name
        while True:
            uName = m2u.core.getEditor().getFreeName(mName)
            _lg.debug("Editor returned '"+uName+ "' as a free name.")
            #if uName is None: return
            if uName != mName:
                _lg.debug(("Name '%s' already in use, Maya needs to find"
                           " a new one.") % mName)
                mName = str(pm.rename(mName, uName))
            if uName == mName: # not 'else', because mName may have changed
                break
        code, edName = m2u.core.getEditor().duplicateObject(str(old), uName, t, r, s)
        # TODO: maybe check the return value of duplicateObject call
        # since we changed the name, we need to select the renamed object or
        # the user will get a MayaNodeError when trying to move the duplicates
        # also subsequent duplicates may depend on a correct selection list
        #reselectNamesList.append(mName)
        
        # this should not happen, because we use getFreeName beforehand
        if code == 3:
            _lg.error(("Renaming the duplicate failed, maya object %s and "
                       "engine object %s are now desynced") % (mName, edName) )
        
        # select waehrend duplicate aufrufen killt den transform wert fuer smart
        # stattdessen muesste entweder ein reselect nach allen duplicates sein
        # ob das geht? oder rename erst nach dem die duplicates erledigt sind
        # duerfte mit dem duplicate callback aber auch problematisch sein
    #pm.select(reselectNamesList, r=True)
    setObjectSyncingState(**_beforeDupSyncState)


########################
# name change tracking #
########################

def _onNameChangedCB(node, prevName, data):
    mfnnode = mapi.MFnDependencyNode(node)
    typeName = mfnnode.typeName()
    
    # we are not interested in renamed shapes or so
    if (not typeName == "transform"):
        #_lg.debug("Not tracking objects of type: %s" % typeName )
        return
    
    newName = str(mfnnode.name())
    if "#" in newName: # those are only temporary name changes to create numbers
        return
    if newName.startswith("__"): # temporary duplicate or import names
        return
    _lg.debug("maya changed name to %s" % newName)
    #print "type is %s" % typeName
    if prevName == newName: #nothing changes really
        return
        
    # TODO: delegate the name-finding functionality to a common function for
    # this and the duplicate callback
    mName = newName # maya's Name
    uName = "" # Engine's Name
    # disable object syncing so internal renames won't trigger a new rename callback
    backupSyncState = getObjectSyncingState()
    setObjectSyncingState(name=False)
    while True:
        uName = m2u.core.getEditor().getFreeName(mName)
        _lg.debug("Editor returned '"+uName+ "' as a free name.")
        #if uName is None: return
        if uName != mName:
            _lg.debug("Name '%s' already in use, need to find a new one." % mName)
            mName = str(pm.rename(mName, uName))
        if uName == mName: # not 'else', because mName may have changed
            break
    setObjectSyncingState(**backupSyncState)
    code,edName = m2u.core.getEditor().renameObject(prevName, mName)
    if code is True: # no problems occured
        return
    else:
        if edName is None:
            # error, no renaming took place, the object was not found or so
            return
    # if we end up here, the editor returned a different name than we desired
    # this should not happen since we "getFreeName" beforehand
    _lg.error( "Renaming failed, maya object %s and engine object %s are now desynced"
               % (mName, edName) )


##################################
# creation and deletion tracking #
##################################

def _onObjectDeletedCB(node, data):
    """ called everytime a (transform) node is deleted """
    mfnnode = mapi.MFnDependencyNode(node)
    name = str(mfnnode.name())
    _lg.debug("maya deleted object %s" % name)
    m2u.core.getEditor().deleteObject(name)


def _onObjectCreatedCB(node, data):
    """ called everytime a node is created
    Currently unused, we use duplicate and import callbacks to track new objects
    that are important for us because they are based on existing assets.
    to send "new objects" to the editor, a much more sophisticated approach
    initiated by the user is necessary anyway.
    """
    #print "object created:"
    #print node
    pass


def _onParentChangedCB(child, parent, data):
    """ called everytime a child gets a new parent

    if parent name is empty '', the child was parented to the world
    
    """
    # TODO: maybe use fullPathName() if namespaces are used for levels 
    nameC = child.partialPathName()
    nameP = parent.partialPathName()
    _lg.debug("child '%s' got new parent '%s'" % (nameC, nameP))
    if nameC == '': # error
        return
    m2u.core.getEditor().parentChildTo(nameC, nameP)