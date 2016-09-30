""" Commands for display layer tracking in maya.

Layer tracking handles hiding, showing and deleting of layers as well as
adding objects to and removing objects from layers.


Actual Callbacks for handling DisplayLayers in Maya are VERY RARE! We
have two callbacks which are "displayLayerChange" which is called when a
layer has been created or deleted. It won't tell us WHICH layer though,
and not WHAT happened.
The other is "displayLayerManagerChange" which is called whenever
something concerning all display layers happens, this includes the user
clicking in the displayLayer UI or so. Again it won't tell us WHICH or
WHAT.

There are a few Commands which we can intercept with the CommandCallback
though, namely "createDisplayLayer" and "editDisplayLayerMembers"

createDisplayLayer is dropped whenever a layer has been created. The
parameters will contain the name of the layer and either nothing
(meaning all selected objects have been added) or the -empty flag if no
objects were added.
The huge problem here is the "name" which comes with that command. It
will always be "layer1"... that alone wouldn't be a problem, because we
could ask the Engine if it accepts that name and, if not, rename maya's
layer. The real problem is, that "layer1" may not exist in maya anymore,
because maya internally renames the layer BEFORE we intercept the command
that a layer has been created at all.
In short: Even this command's information is more or less useless for us
because we will never be able to know from here, which layer was created,
how it is named now and so on. At least not with a lot of fancy magic
data gathering...

editDisplayLayerMembers on the other hand seems to be the only guy in
maya's whole display layer arsenal, that really does what it says and
always provides us with the list of objects that have been added or
removed from the layer.

"""

import sys
import logging

import pymel.core as pm
import pymel.api as mapi

import m2u

_lg = logging.getLogger(__name__)

this = sys.modules[__name__]
"""this is required because the script jobs are in mayas namespace,
so absolute paths to functions called inside SJs are required.
Since the path to this module may change, it is easier to get the
real path at runtime instead of hardcoding something.
"""

this._is_layer_syncing = False
this._layer_script_jobs = []
this._name_tracking_disabled_internally = False

# The callback IDs are returned from maya and are used to delete the callbacks.
this._on_command_executed_cb_id = None
this._on_display_layer_deleted_cb_id = None
this._on_name_changed_cb_id = None


nullMObject = mapi.OpenMaya.MObject()
"""Some callback functions expect a specific node to create a callback
for. Passing a nullMObject makes some of those functions track all nodes
instead.
"""


def set_layer_syncing(sync):
    this._is_layer_syncing = sync
    if sync:
        _create_layer_tracker()
    else:
        _delete_layer_tracker()


def is_layer_syncing():
    return this._is_layer_syncing


def _create_layer_tracker():
    this._on_command_executed_callback_id = (
        mapi.MCommandMessage.addCommandCallback(_on_command_executed_cb))

    node_type = "displayLayer"
    this._on_display_layer_deleted_cb_id = (
        mapi.MDGMessage.addNodeRemovedCallback(
            _on_display_layer_deleted_cb, node_type))

    this._on_name_changed_callback_id = (
        mapi.MNodeMessage.addNameChangedCallback(nullMObject,
                                                 _on_name_changed_cb))

    _create_all_layer_script_jobs()


def _delete_layer_tracker():
    if this._on_command_executed_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_command_executed_cb_id)
        this._on_command_executed_cb_id = None

    if this._on_display_layer_deleted_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_display_layer_deleted_cb_id)
        this._on_display_layer_deleted_cb_id = None

    if this._on_name_changed_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_name_changed_cb_id)
        this._on_name_changed_cb_id = None

    _delete_layer_script_jobs()


#######################
# visibility tracking #
#######################

def _create_all_layer_script_jobs():
    """ Delete all script jobs and create new ones. That way we don't
    have to take care if a layer already has a job or not.
    """
    _delete_layer_script_jobs()
    for layer in pm.ls(type="displayLayer")[1:]:
        # The first layer is the default layer, we ignore it.
        _create_layer_script_job(layer)


def _create_layer_script_job(layer):
    if not layer.exists():
        return
    layer_name = layer.name()
    sj_call = __name__ + '.on_layer_changed_sj("{0}")'.format(layer_name)
    sj_id = pm.scriptJob(attributeChange=[layer_name + '.visibility', sj_call])
    this._layer_script_jobs.append(sj_id)


def on_layer_changed_sj(layer_name):
    vis = pm.getAttr(layer_name + ".visibility")
    if vis:
        m2u.core.editor.unhide_layer(layer_name)
    else:
        m2u.core.editor.hide_layer(layer_name)


def _delete_layer_script_jobs():
    for sj in this._layer_script_jobs:
        pm.scriptJob(kill=sj, force=True)
    this._layer_script_jobs = []


######################################
# create, delete and member tracking #
######################################

def _on_command_executed_cb(cmd, data):
    if cmd.startswith("createDisplayLayer"):
        _on_create_display_layer(cmd)
    elif cmd.startswith("editDisplayLayerMembers"):
        _on_edit_display_layer_members(cmd)


def _on_name_changed_cb(node, prev_name, data):
    """ Called whenever a displayLayer-node's name was changed.
    Display layer names are currently not checked for validity or
    uniqueness.

    Name change on a display layer will go hand in hand with all
    attributes being "changed". That means our visibility script job
    will fire - with a name that doesn't exist anymore, resulting in
    an AttributeError.

    To prevent that, disable the script jobs when a name change is
    detected and enable it at the end of this function, no matter what
    happened, thus the while loop with breaks instead of using plain
    return statements.
    """
    _delete_layer_script_jobs()

    while True:
        if this._name_tracking_disabled_internally:
            break

        mfnnode = mapi.MFnDependencyNode(node)
        type_name = mfnnode.typeName()

        if (not type_name == "displayLayer"):
            break

        new_name = str(mfnnode.name())
        if "#" in new_name:
            # Those are only temporary name changes to create numbers.
            break
        if len(prev_name) == 0:
            # The empty string is a sign that a new layer has been
            # created. It will now be renamed probably two times, we
            # don't want those name changes to be propagated, so we
            # disable name tracking here. It will be enabled again at
            # the end of the _on_create_display_layer function.
            this._name_tracking_disabled_internally = True
            break

        if prev_name == new_name:
            # Nothing changes really
            break

        _lg.debug("Renamed layer '{0}' to '{1}'.".format(prev_name, new_name))
        # TODO: If the Editor assigns another name, we don't care for now.
        m2u.core.editor.rename_layer(prev_name, new_name)
        break
    _create_all_layer_script_jobs()


def _on_create_display_layer(cmd):
    """ Called when a display layer was created. This is often done in
    conjunction with adding objects to that new layer.

    The cmd will look something like this (all selected objects added):

        createDisplayLayer "-name" "layer1" "-number" 1 "-nr";

    Or so (no objects added):

        createDisplayLayer "-name" "layer1" "-number" 1 "-empty";

    Problem is: This command will always have the name "layer1" which
    can't be created if a layer named "layer1" already exists.
    The layer "layer1" probably doesn't even exist in maya anymore,
    because maya's renaming of the layer takes place BEFORE this
    command is recognized.
    So even if a "layer1" exists, it might not be the one just created.

    We know that a new layer has been created and that the selected
    objects are now its members. So we can ask one of the selected
    objects about its current layer, which will be the new layer.

    This of course only works when the selected objects were added to
    the layer. Otherwise this would be an empty layer, which we can
    ignore.
    """
    while True:
        if "-empty" in cmd:
            # Yeah, not interested in empty layers.
            break

        sel = pm.selected()
        if len(sel) < 1:
            # There was no selection, so it was an empty layer too.
            break

        obj = sel[0]
        layers = obj.listConnections(type="displayLayer")
        layer = layers[0]
        objects = [x.name() for x in sel]
        _lg.debug("New layer is '{0}', with objects {1}"
                  .format(layer.name(), objects))
        m2u.core.editor.add_objects_to_layer(layer.name(), objects, True)
        break

    this._name_tracking_disabled_internally = False
    _create_all_layer_script_jobs()


def _on_edit_display_layer_members(cmd):
    """ Called when objects were added or removed from a display layer.

    The cmd will look something like this:

        editDisplayLayerMembers "-noRecurse" "layer2" {"pCube1"};

    If the layer's name is "defaultLayer" the objects were removed from
    any real named layer.

    Note: The `-noRecurse` `-nr` parameter is not checked, because it
      is always present in default maya behaviour and since the list
      of objects is passed, it probably isn't necessary.
    """
    if "-query" in cmd:
        # Query happens when the user right-clicks on a layer etc.
        return

    # Find the no-parameter quoted string, it will be the layer's name.
    # TODO: Can we make this clearer with a regexp?
    name_start = 0
    for i in range(0, len(cmd)):
        if cmd[i] == '"' and cmd[i+1] != '-' and cmd[i+1] != ' ':
            name_start = i + 1
            break
    name_end = cmd.find('"', name_start)
    name = cmd[name_start: name_end]

    # Extract all object names from the text.
    list_start = cmd.find("{")
    list_end = cmd.find("}")
    cnt = cmd[list_start + 2: list_end - 1]
    names = cnt.split('","')
    names2 = "["+(','.join(names))+"]"

    if name == "defaultLayer":
        _lg.debug("Removed objects from layers: " + names2)
        m2u.core.editor.remove_objects_from_all_layers(names)
    else:
        _lg.debug("layer '" + name + "' added children " + names2)
        m2u.core.editor.add_objects_to_layer(name, names, True)
    _create_all_layer_script_jobs()


def _on_display_layer_deleted_cb(node, data):
    """ Called when a display layer was deleted.
    """
    mfnnode = mapi.MFnDependencyNode(node)
    name = str(mfnnode.name())
    _lg.debug("Maya deleted display layer '%s'" % name)
    m2u.core.editor.delete_layer(name)
    _create_all_layer_script_jobs()
