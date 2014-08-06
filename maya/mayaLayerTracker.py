""" commands for display layer tracking in maya

Layer tracking handles hiding, showing and deleting of layers as well as adding objects to and removing objects from layers.


Actual Callbacks for handling DisplayLayers in Maya are VERY RARE! We have two
callbacks which are "displayLayerChange" which is called when a layer has been
created or delted. It won't tell us WHICH layer though, and not WHAT happened.
The other is "displayLayerManagerChange" which is called whenever something
concerning all display layers happens, this includes the user clicking in the
displayLayer UI or so. Again it won't tell us WHICH or WHAT.

There are a few Commands which we can intercept with the CommandCallback namely
"createDisplayLayer" and "editDisplayLayerMembers"

createDisplayLayer is dropped whenever a layer has been created. The parameters
will contain the name of the layer and either nothing (meaning all selected objects
have been added) or the -empty flag if no objects were added.
The huge problem here is the "name" which comes with that command. It will
always be "layer1"... that alone wouldn't be a problem, because we could ask
the Engine if it accepts that name and, if not, rename maya's layer. The real
problem is, that "layer1" may not exist in maya anymore, because maya internally
renames the layer BEFORE we intercept the command that a layer has been created
at all. In short: even this command's information is more or less useless for us
because we will never be able to know from here, which layer was created, how it
is named now and so on. At least not with a lot of fancy magic data gathering...

editDisplayLayerMembers on the other hand seems to be the only guy in maya's
whole display layer arsenal, that really does what it says and always provides
us with the list of objects that have been added or removed from the layer.

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

__bLayerSync = False
def setLayerSyncing( sync ):
    global __bLayerSync
    __bLayerSync = sync
    if sync:
        createLayerTracker()
    else:
        deleteLayerTracker()

def isLayerSyncing():
    return __bLayerSync

# the callback IDs are returned from maya and are used to delete the callbacks
_onCommandExecutedCBid = None
_onDisplayLayerDeletedCBid = None
_onNameChangedCBid = None

nullMObject = mapi.OpenMaya.MObject()

_nameTrackingDisabledInternally = False

def createLayerTracker():
    global _onCommandExecutedCBid
    _onCommandExecutedCBid = mapi.MCommandMessage.addCommandCallback(
       _onCommandExecutedCB)
    global _onDisplayLayerDeletedCBid
    nodeType = "displayLayer"
    _onDisplayLayerDeletedCBid = mapi.MDGMessage.addNodeRemovedCallback(
       _onDisplayLayerDeletedCB, nodeType)
    global _onNameChangedCBid
    _onNameChangedCBid = mapi.MNodeMessage.addNameChangedCallback( nullMObject,
        _onNameChangedCB)
    
    _createAllLayerScriptJobs()

def deleteLayerTracker():
    global _onCommandExecutedCBid
    if _onCommandExecutedCBid is not None:
        mapi.MMessage.removeCallback(_onCommandExecutedCBid)
        _onCommandExecutedCBid = None
    global _onDisplayLayerDeletedCBid
    if _onDisplayLayerDeletedCBid is not None:
        mapi.MMessage.removeCallback(_onDisplayLayerDeletedCBid)
        _onDisplayLayerDeletedCBid = None
    global _onNameChangedCBid
    if _onNameChangedCBid is not None:
        mapi.MMessage.removeCallback(_onNameChangedCBid)
        _onNameChangedCBid = None
    _deleteLayerScriptJobs()


#######################
# visibility tracking #
#######################
_layerScriptJobs = list()
def _createAllLayerScriptJobs():
    """ simply delete all script jobs and create new ones
    that way we don't have to take care if a layer already has a job or not
    """
    _deleteLayerScriptJobs()
    for layer in pm.ls(type="displayLayer")[1:]:
        _createLayerScriptJob(layer)

def _createLayerScriptJob(layer):
    global _layerScriptJobs
    if not layer.exists():
        return
    name = layer.name()
    sj = pm.scriptJob( attributeChange=[name+'.visibility',
                            __name__+".onLayerChangedSJ(\""+name+"\")"] )
    _layerScriptJobs.append(sj)


def onLayerChangedSJ(obj):
    #if not pm.general.objExists(obj)
    #    return
    vis = pm.getAttr(obj+".visibility")
    if vis:
        m2u.core.getEditor().unhideLayer(obj)
    else:
        m2u.core.getEditor().hideLayer(obj)


def _deleteLayerScriptJobs():
    global _layerScriptJobs
    for sj in _layerScriptJobs:
        pm.scriptJob( kill=sj, force = True)
    _layerScriptJobs[:]=[] #empty the list


######################################
# create, delete and member tracking #
######################################
    
# NOTE: for CommandCallback
# Since calling more and more functions with all the same callback string can reduce
# performance significantly, there should only be ONE CommandCallback for all
# of m2u. Wwe should move this callback to some common file and register only the
# functions for specific strings.
def _onCommandExecutedCB(cmd, data):
    if cmd.startswith("createDisplayLayer"):
        _onCreateDisplayLayer(cmd)
    elif cmd.startswith("editDisplayLayerMembers"):
        _onEditDisplayLayerMembers(cmd)


def _onNameChangedCB(node, prevName, data):
    """ called whenever a displayLayer-node's name was changed
    Display layer names are currently not checked for validity or uniqueness.
    """
    # name change on a display layer will go hand in hand with all attributes
    # being "changed". That means our visibility script job will fire...
    # with a name that doesn't exist anymore? I get a maya AttributeError.
    # To prevent that, disable the script jobs when a name change is detected
    # and enable it at the end of this function, no matter what happened, thus
    # the while loop with breaks instead of plain return statements
    _deleteLayerScriptJobs()
    global _nameTrackingDisabledInternally
    while True:
        if _nameTrackingDisabledInternally:
            #_lg.debug("layer name tracking disabled internally")
            break
        
        mfnnode = mapi.MFnDependencyNode(node)
        typeName = mfnnode.typeName()
        
        if (not typeName == "displayLayer"):
            break
        
        newName = str(mfnnode.name())
        #_lg.debug("pre check renamed layer '"+prevName+"' to '"+newName+"'")
        if "#" in newName: # those are only temporary name changes to create numbers
            break
        if len(prevName) == 0:
            # the empty string is a sign that a new layer has been created.
            # it will now be renamed probably two times, we don't want those name
            # changes to be propagated, so we disable name tracking here. It will be
            # enabled again at the end of the _onCreateDisplayLayer function.
            _nameTrackingDisabledInternally = True
            #_lg.debug("old layer name was empty, disabling name tracking")
            break
            
        if prevName == newName: #nothing changes really
            break
        
        _lg.debug("renamed layer '"+prevName+"' to '"+newName+"'")
        #TODO: If the Editor assigns another name, we don't care for now.
        m2u.core.getEditor().renameLayer(prevName, newName)
        break
    _createAllLayerScriptJobs()


def _onCreateDisplayLayer(cmd):
    """ called when a display layer was created. This is often done in conjunction
    with adding objects to that new layer.
    
    the cmd will look something like this (all selected objects added):
    createDisplayLayer "-name" "layer1" "-number" 1 "-nr";
    or so (no objects added):
    createDisplayLayer "-name" "layer1" "-number" 1 "-empty";

    """
    # Problem is: this command will always have the name "layer1" which can't
    # be created if a layer named "layer1" already exists in UE
    # The layer "layer1" probably doesn't even exist in maya anymore, because
    # mayas renaming of the layer takes place BEFORE this command is recognized.
    # so if a "layer1" exists, it might not be the one just created.

    # we know that a new layer has been created and that the selected objects
    # are now its members. So we can ask one of the selected objects about
    # its current layer, that will be the new layer.

    # This of course only works when the selected objects were added to the layer
    # but we don't really care about syncing empty layers anyway, do we?

    while True:
        if "-empty" in cmd: # yeah, not interested in empty layers
            break
        
        sel = pm.selected()
        if len(sel)<1: # there was no selection, so it was an empty layer too
            break
        
        obj = sel[0]
        layers = obj.listConnections(type="displayLayer")
        layer = layers[0]
        objects = [x.name() for x in sel]
        _lg.debug("new layer is '"+layer.name()+"' with objects "+str(objects))
        m2u.core.getEditor().addObjectsToLayer(layer, objects, True)
        
        break
    
    global _nameTrackingDisabledInternally
    _nameTrackingDisabledInternally = False
    _createAllLayerScriptJobs()


def _onEditDisplayLayerMembers(cmd):
    """ called when objects were added or removed from a display layer.

    the cmd will look something like this:
    editDisplayLayerMembers "-noRecurse" "layer2" {"pCube1"};
    if the layer's name is "defaultLayer" the objects were removed from
    any real named layer.
    """
    # NOTE: the -noRecurse -nr parameter is not checked, because it is always present
    # in default maya behaviour and since the list of objects is passed, it
    # probably isn't necessary, but I would need to check that.
    if "-query" in cmd:
        # query happens when the user right-clicks on a layer etc.
        return
    # find the no-parameter quoted string, it will be the layer's name
    nameStart = 0
    for i in range(0,len(cmd)):
        if cmd[i]=='"' and cmd[i+1]!='-' and cmd[i+1]!=' ':
            nameStart = i+1
            break
    nameEnd = cmd.find('"', nameStart)
    name = cmd[nameStart:nameEnd]
    # extract all object names from the text
    listStart = cmd.find("{")
    listEnd = cmd.find("}")
    cnt = cmd[listStart+2:listEnd-1]
    names = cnt.split('","')
    names2 = "["+(','.join(names))+"]"
    
    if name == "defaultLayer":
        _lg.debug("removed objects from layers: "+names2)
        m2u.core.getEditor().removeObjectsFromAllLayers(names)
    else:
        _lg.debug("layer '"+name+"' added children "+names2)
        m2u.core.getEditor().addObjectsToLayer(name, names, True)
    _createAllLayerScriptJobs()


def _onDisplayLayerDeletedCB(node, data):
    """ called when a display layer was deleted.
    """
    mfnnode = mapi.MFnDependencyNode(node)
    name = str(mfnnode.name())
    _lg.debug("maya deleted display layer '%s'" % name)
    m2u.core.getEditor().deleteLayer(name)
    _createAllLayerScriptJobs()



