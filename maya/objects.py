""" Commands for object tracking in maya.

Object tracking works by creating one callback for 'selection changed'
tracking which in turn will create script jobs for all selected objects
to survey their transformation values and on a change will execute a
sync.

All object script jobs will be removed when the selection changed, after
which new SJs are created.

Other callbacks are created to track if objects are created, deleted,
renamed, parent-child relationships change, etc.

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

this._is_object_syncing = False
this._object_script_jobs = []

# The callback IDs are returned from maya and are used to delete the callbacks.
this._on_selection_changed_cb_id = None
this._on_before_duplicate_cb_id = None
this._on_after_duplicate_cb_id = None
this._on_name_changed_cb_id = None
this._on_object_created_cb_id = None
this._on_object_deleted_cb_id = None
this._on_parent_changed_cb_id = None


RADIAN_TO_DEGR = 57.2957795
DEGR_TO_RADIAN = 0.0174532925


#########################
# convenience functions #
#########################

def get_transformation_from_obj(obj):
    # TODO: clean up and generalize this function.
    # TODO: we maybe should start piping a 'transformed' transformation
    #   matrix between functions / programs, instead of 3 tuples of 3 floats.
    """ Get three float tuples for translate, rotate and scale of the
    object.

    Args:
        obj (Node): A maya pymel node instance.

    Returns:
        ((f,f,f),(f,f,f),(f,f,f)): Tuple with translation, rotation,
            and scale float tuples.
    """

    # TODO: This function should automatically consider the correct
    #   swizzling and rotation order conversion for the axis-up-space that
    #   is set in maya or the UI.

    # TODO: Currently conversion from maya to UDK/UE4 space is hard coded
    #   here. This will not work for Unity and the like. This functionality
    #   has to be reworked.


    # If the engine supports nested transforms, world-space transforms
    # will mess up the result.
    use_world_space = not m2u.core.editor.supports_parenting()

    # The translate values in the matrix will always reflect the TRUE
    # translation while parenting and pivots mess up the the other results
    mat = pm.xform(obj, query=True, m=True, ws=use_world_space)
    #tx,ty,tz = pm.xform(obj,query=True, ws=useWorldSpace, t=True)
    tx, ty, tz = (mat[12],mat[13],mat[14])
    #tx,ty,tz = translationMayaToUDK(t)
    #tx,ty,tz = (-tz,tx,ty) # y-up
    #tx,ty,tz = (ty,tx,tz) # z-up
    tx, ty, tz = (tx, -ty, tz)  # z-up as fbx from udk

    rx, ry, rz = pm.xform(obj, query=True, ws=use_world_space, ro=True)
    #rx,ry,rz = rotationMayaToUDK(r) #script job namespace problem

    # maya y-up
    # udk has a different rotation order (ZXY), so we transform the stuff here
    # mrot = mapi.MEulerRotation(rx*DEGR_TO_RADIAN,ry*DEGR_TO_RADIAN,rz*DEGR_TO_RADIAN)
    # newrot = mrot.reorder(mapi.MEulerRotation.kZXY)
    # rx,ry,rz = (newrot.x,newrot.y,newrot.z)
    # rx,ry,rz = (rx*RADIAN_TO_DEGR, ry*RADIAN_TO_DEGR, rz*RADIAN_TO_DEGR)
    # rx,ry,rz = (rx,-ry,-rz)

    # maya z-up
    #rx,ry,rz = (rx,-rz,ry) # z-up (same as max)
    rx, ry, rz = (-ry, -rz, rx)  # z-up as fbx from udk

    sx, sy, sz = pm.xform(obj, query=True, r=True, s=True)
    #sx,sy,sz = (sz,sx,sy) # y-up
    #sx,sy,sz = (sy,sx,sz) # z-up (as max)
    sx, sy, sz = (sx, sy, sz)  # z-up as fbx from udk

    return ((tx, ty, tz), (rx, ry, rz), (sx, sy, sz))


############################
# tracking setup functions #
############################

def set_object_syncing(sync):
    this._is_object_syncing = sync
    if sync:
        _create_object_tracker()
    else:
        _delete_object_tracker()


def is_object_syncing():
    return this._is_object_syncing


def get_object_syncing_state():
    """ Get a dictionary mapping which object trackers are active.
    The dictionary contains name:bool pairs that can be fed back into
    the func:`set_object_syncing_state()` function.
    """
    states = {
        "selection": bool(this._on_selection_changed_cb_id),
        "duplicate": bool(this._on_before_duplicate_cb_id),
        "name": bool(this._on_name_changed_cb_id),
        "existence": bool(this._on_object_deleted_cb_id),
        "relationship": bool(this._on_parent_changed_cb_id),
    }
    return states


def set_object_syncing_state(**kwargs):
    """ Activate or disable specific trackers.
    """
    if "selection" in kwargs:
        if kwargs["selection"]:
            _create_selection_tracker()
        else:
            _delete_selection_tracker()
    if "duplicate" in kwargs:
        if kwargs["duplicate"]:
            _create_duplicate_tracker()
        else:
            _delete_duplicate_tracker()
    if "name" in kwargs:
        if kwargs["name"]:
            _create_name_tracker()
        else:
            _delete_name_tracker()
    if "existence" in kwargs:
        if kwargs["existence"]:
            _create_existence_tracker()
        else:
            _delete_existence_tracker()
    if "relationship" in kwargs:
        if kwargs["relationship"]:
            _create_relationship_tracker()
        else:
            _delete_relationship_tracker()


nullMObject = mapi.OpenMaya.MObject()
"""Some callback functions expect a specific node to create a callback
for. Passing a nullMObject makes some of those functions track all nodes
instead.
"""


def _create_object_tracker():
    """ Create all callbacks that track object-changes.
    """
    _create_selection_tracker()
    _create_duplicate_tracker()
    _create_name_tracker()
    _create_existence_tracker()
    _create_relationship_tracker()


def _delete_object_tracker():
    """ Delete all callbacks that track object-changes.
    """
    _delete_selection_tracker()
    _delete_duplicate_tracker()
    _delete_name_tracker()
    _delete_existence_tracker()
    _delete_relationship_tracker()


# These functions always delete old trackers before creating the new
# ones, just to make sure there aren't suddenly two callbacks doing the
# same. The alternative would be to check if the callbacks are None, but
# we assume that we always want to create NEW callbacks for simplicity.


def _create_selection_tracker():
    _delete_selection_tracker()
    this._on_selection_changed_cb_id = mapi.MEventMessage.addEventCallback(
        "SelectionChanged", _on_selection_changed_cb)
    # Automatically create tracking script jobs on the current selection
    # but don't emit "selection changed" or it will be emitted very often
    # during tracking-disabling operations like duplication and name-
    # changing.
    _create_object_script_jobs_no_sel_changed()


def _create_duplicate_tracker():
    _delete_duplicate_tracker()
    this._on_before_duplicate_cb_id = (
        mapi.MModelMessage.addBeforeDuplicateCallback(_on_before_duplicate_cb))
    this._on_after_duplicate_cb_id = (
        mapi.MModelMessage.addAfterDuplicateCallback(_on_after_duplicate_cb))


def _create_name_tracker():
    _delete_name_tracker()
    this._on_name_changed_cb_id = (
        mapi.MNodeMessage.addNameChangedCallback(nullMObject,
                                                 _on_name_changed_cb))


def _create_existence_tracker():
    _delete_existence_tracker()
    nodeType = "transform"  # TODO: maybe use "dagObject" and filter afterwards
    # this._on_object_created_cb_id = mapi.MDGMessage.addNodeAddedCallback(
    #    _on_object_created_cb, nodeType)
    this._on_object_deleted_cb_id = mapi.MDGMessage.addNodeRemovedCallback(
        _on_object_deleted_cb, nodeType)


def _create_relationship_tracker():
    _delete_relationship_tracker()
    # _onParentChangedCBid = mapi.MDagMessage.addAllDagChangesCallback(
    this._on_parent_changed_cb_id = mapi.MDagMessage.addParentAddedCallback(
        _on_parent_changed_cb)


def _delete_selection_tracker():
    if this._on_selection_changed_cb_id is not None:
        _delete_object_sjs()
        mapi.MEventMessage.removeCallback(this._on_selection_changed_cb_id)
        this._on_selection_changed_cb_id = None


def _delete_duplicate_tracker():
    if this._on_after_duplicate_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_after_duplicate_cb_id)
        mapi.MMessage.removeCallback(this._on_before_duplicate_cb_id)
        this._on_after_duplicate_cb_id = None
        this._on_before_duplicate_cb_id = None


def _delete_name_tracker():
    if this._on_name_changed_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_name_changed_cb_id)
        this._on_name_changed_cb_id = None


def _delete_existence_tracker():
    if this._on_object_created_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_object_created_cb_id)
        this._on_object_created_cb_id = None
    if this._on_object_deleted_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_object_deleted_cb_id)
        this._on_object_deleted_cb_id = None


def _delete_relationship_tracker():
    if this._on_parent_changed_cb_id is not None:
        mapi.MMessage.removeCallback(this._on_parent_changed_cb_id)
        this._on_parent_changed_cb_id = None


###########################
# transformation tracking #
###########################

def _on_selection_changed_cb(data):
    """ Creates the object tracking script jobs and tells the editor to
    update the selection.
    """
    m2u.core.editor.deselect_all()
    _create_object_script_jobs_no_sel_changed()
    names_list = [obj.name() for obj in pm.selected()]
    m2u.core.editor.select_by_names(names_list)


def _create_object_script_jobs_no_sel_changed():
    """ Creates the object tracking script jobs without emitting a
    `selection changed` to the editor.
    """
    _delete_object_sjs()

    # If we can NOT use parenting, we need to make sure all the objects
    # that are children of the selected objects in maya are explicitly
    # synced. If parenting is possible, the transforms will be implicitly
    # synced because they are relative to the parent in the editor anyway.

    # We need to filter out objects that are selected and have parents
    # selected since we will sync all children of selected objects.
    # Those objects would be double-synced otherwise.
    # Note: It may be faster to double-sync some objects than to check
    #   long lists of child objects...
    selection = pm.selected()
    only_parent_list = selection
    if not m2u.core.editor.supports_parenting():
        for obj in selection:
            children = pm.listRelatives(obj,
                                        allDescendents=True,
                                        noIntermediate=True,
                                        type="transform")
            for child in children:
                if child in selection:
                    only_parent_list.remove(child)

    for obj in only_parent_list:
        # Only track transform-nodes.
        if obj.nodeType() != "transform":
            continue
        # Since the sj is in maya namespace, we need the full qualifier
        sj_call = __name__ + '.on_object_changed_sj("{0}")'.format(obj.name())
        sj_id = pm.scriptJob(attributeChange=[obj.name()+'.matrix', sj_call])
        this._object_script_jobs.append(sj_id)


def on_object_changed_sj(obj):
    all_dep_objs = [obj]
    if not m2u.core.editor.supports_parenting():
        children = pm.listRelatives(obj,
                                    allDescendents=True,
                                    noIntermediate=True,
                                    type="transform")
        all_dep_objs.extend(children)
    for node in all_dep_objs:
        t, r, s = this.get_transformation_from_obj(node)
        m2u.core.editor.transform_object(node, t, r, s)


def _delete_object_sjs():
    for sj_id in this._object_script_jobs:
        pm.scriptJob(kill=sj_id, force=True)
    this._object_script_jobs = []


########################
# duplication tracking #
########################

this._before_dup_selection = None
this._before_dup_sync_state = None


def _on_before_duplicate_cb(data):
    """Save the selection to know which objects are going to be
    duplicated.
    """
    this._before_dup_selection = pm.selected()
    # We have to disable rename and parent tracking, so we don't try
    # to make stuff with intermediate objects.
    this._before_dup_sync_state = get_object_syncing_state()
    set_object_syncing_state(name=False, selection=False, relationship=False)


def _on_after_duplicate_cb(data):
    """Go through selection (the duplicated objects), get associated
    original object from pre duplicate selection and send the pair to
    the Editor for duplication.

    """
    after_dup_sel = pm.selected()
    if len(after_dup_sel) != len(this._before_dup_selection):
        _lg.error("Could not sync duplication, originals and results lists "
                  "are of different lengths.")
        return

    dup_infos = []
    # reselect_names_list = list()
    for old, new in zip(this._before_dup_selection, after_dup_sel):
        t, r, s = get_transformation_from_obj(new)
        # Now get an unused name from the editor.
        # If the names mismatch, we need to rename the object in maya.
        # The name maya actually assigns to the object may change again
        # so we need to do this until maya and the editor agree upon
        # a name.
        m_name = str(new)  # maya's Name
        ed_name = ""  # Engine's Name
        while True:
            ed_name = m2u.core.editor.get_free_name(m_name)
            _lg.debug("Editor returned '{0}' as a free name.".format(ed_name))
            if ed_name != m_name:
                _lg.debug("Name '{0}' already in use, Maya needs to find"
                          " a new one.".format(m_name))
                m_name = str(pm.rename(m_name, ed_name))
            if ed_name == m_name:  # not 'else', because m_name may have changed
                break

        dup_info = {'original': str(old),
                    'name': ed_name,
                    'translation': t,
                    'rotation': r,
                    'scale': s}
        dup_infos.append(dup_info)

    results = m2u.core.editor.duplicate_objects(dup_infos)

    for index, code, ed_name in enumerate(results):
        m_name = dup_infos[index]['']
        if code == "NotFound":
            _lg.error("Duplication failed on {0}, original object could not "
                      "be found.".format(m_name))
        elif code == "Renamed":
            # This should not happen, because we used get_free_name beforehand.
            _lg.error("Renaming the duplicate failed, maya object '{0}' and "
                      "engine object '{1}' are now desynced."
                      .format(m_name, ed_name))
        elif code == "Failed":
            _lg.error("Duplication failed on {0}, unknown reason."
                      .format(m_name))

    # Selecting during duplication will kill the transform value for
    # smart-duplicate. We would have to do a reselect after ALL
    # duplicates, or do the renaming after all the duplication is
    # done. But this could get complicated with duplicate callbacks.

    # since we changed the name, we need to select the renamed object or
    # the user will get a MayaNodeError when trying to move the duplicates
    # also subsequent duplicates may depend on a correct selection list
    # pm.select(reselect_names_list, r=True)
    set_object_syncing_state(**this._before_dup_sync_state)


########################
# name change tracking #
########################

def _on_name_changed_cb(node, prev_name, data):
    mfnnode = mapi.MFnDependencyNode(node)
    type_name = mfnnode.typeName()

    # We are not interested in renamed shapes or so
    if (not type_name == "transform"):
        # _lg.debug("Not tracking objects of type: %s" % type_name )
        return

    new_name = str(mfnnode.name())
    if "#" in new_name:
        # Those are only temporary name changes to create numbers.
        return
    if new_name.startswith("__"):
        # Temporary duplicate or import names.
        return
    _lg.debug("maya changed name to %s" % new_name)

    if prev_name == new_name:
        # Nothing changes really
        return

    # TODO: delegate the name-finding functionality to a common function for
    # this and the duplicate callback
    m_name = new_name # maya's Name
    ed_name = "" # Engine's Name

    # Disable object syncing so internal renames won't trigger a new
    # rename callback.
    backup_sync_state = get_object_syncing_state()
    set_object_syncing_state(name=False)
    while True:
        ed_name = m2u.core.editor.get_free_name(m_name)
        _lg.debug("Editor returned '{0}' as a free name.".format(ed_name))
        if ed_name != m_name:
            _lg.debug("Name '{0}' already in use, Maya needs to find"
                      " a new one.".format(m_name))
            m_name = str(pm.rename(m_name, ed_name))
        if ed_name == m_name:  # not 'else', because m_name may have changed
            break
    set_object_syncing_state(**backup_sync_state)
    code, ed_name = m2u.core.editor.rename_object(prev_name, m_name)
    if code is True:
        # No problems occured
        return
    else:
        if ed_name is None:
            # error, no renaming took place, the object was not found or so
            return
    # If we end up here, the editor returned a different name than we
    # desired this should not happen since we "getFreeName" beforehand
    _lg.error("Renaming failed, maya object '{0}' and engine object '{1}' "
              "are now desynced.".format(m_name, ed_name))


##################################
# creation and deletion tracking #
##################################

def _on_object_deleted_cb(node, data):
    """ Called everytime a (transform) node is deleted. """
    mfnnode = mapi.MFnDependencyNode(node)
    name = str(mfnnode.name())
    _lg.debug("maya deleted object %s" % name)
    m2u.core.editor.delete_object(name)


def _on_object_created_cb(node, data):
    """ Called everytime a node is created.
    Currently unused. We use duplicate and import callbacks to track new
    objects that are important for us, because they are based on existing
    assets.
    To send "new objects" to the editor, a much more sophisticated approach
    initiated by the user is necessary anyway.
    """
    # print "object created:"
    # print node
    pass


def _on_parent_changed_cb(child, parent, data):
    """ Called everytime a child gets a new parent.

    If parent name is empty '', the child was parented to the world.

    """
    # TODO: maybe use fullPathName() if namespaces are used for levels
    child_name = child.partialPathName()
    parent_name = parent.partialPathName()
    _lg.debug("Child '{0}' got new parent '{1}'".format(child_name,
                                                        parent_name))
    if child_name == '':
        # error
        return
    m2u.core.editor.parent_child_to(child_name, parent_name)
