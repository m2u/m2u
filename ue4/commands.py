"""Functions for commands which interact with UE4.

Commands will be issued by sending messages through the TCP port.

"""

import os
import logging
import json

from m2u import core
from m2u.helper.objects import ObjectInfo
from . import connection

_lg = logging.getLogger(__name__)


def transform_object(obj_name, t=None, r=None, s=None):
    """Transform an object with absolute transformations.

    :param obj_name: name of the object to modify
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change

    """
    t = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    r = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    s = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    msg = ("TransformObject {name} {t} {r} {s}"
           .format(name=obj_name, t=t, r=r, s=s))
    return connection.send_message(msg)


def transform_camera(x, y, z, rx, ry, rz, cam_identifier="All"):
    """Set the Camera in UEd

    :param x,y,z: position for the camera
    :param rx,ry,rz: rotation for the camera
    :param cam_identifier: string that explains which viewports to set

    By default, all Viewport Cameras will be set to the provided
    position and rotation.

    """
    # TODO: CamIdentifier is not yet used in m2uPlugin, possible values
    #   should be: All, AllPersp, AllTop, AllFront, AllSide, or an Index
    #   specifying a specific viewport. Or a name for a camera.
    msg = ("TransformCamera {x} {y} {z} {rx} {ry} {rz} {cam_identifier}"
           .format(**locals()))
    return connection.send_message(msg)


def delete_selected():
    msg = ("DeleteSelected")
    return connection.send_message(msg)


def rename_object(name, new_name):
    """Try to assign a new name to an object.

    :param name: current name of the object
    :param new_name: desired name for the object

    :return: tuple (bool,string) True if no problem occured,
        False otherwise. If False, the string will be the name the
        Editor assigned or None, if no renaming took place.

    You can use :func:`get_free_name` to find a name that is unused in
    the Editor prior to actually renaming the object.
    """
    msg = ("RenameObject %s %s" % (name, new_name))
    result = connection.send_message(msg)
    if result == "NotFound":
        _lg.error("No object with name '%s' exists", name)
        return (False, None)
    if result == new_name:
        return (True, None)
    else:
        # The object was (probably) renamed! but the editor changed the name...
        _lg.warn("Rename returned a different name than desired "
                 "('%s' instead of '%s').", result, new_name)
        return (False, result)


def duplicate_objects(dup_infos):
    """Duplicate an object with optional transformations.

    Args:
        dup_infos (list[dict]): A list of duplication infos.
            Each info is a dictionary, containing the following data:
            original (str): Name of the object to duplicate.
            name (str): Desired name for the duplicate.
            translation (f,f,f): Translation float tuple or None if not
                to change.
            rotation (f,f,f): Rotation float tuple or None if not to
                change.
            scale (f,f,f): 3d scale float tuple or None if not to change.

    Returns:
        list[tuple (str, str)]: The first element of each tuple
            contains the return 'code' of the operation, which can be
            - 'Ok' If no problem occured.
            - 'NotFound' If the original could not be found.
            - 'Renamed' If the name was changed by the editor.
            - 'Failed' If something else problematic happened.
           The second element is None, unless the editor 'Renamed' the
           object, in which case it contains the editor-assigned name.

    If the return value is 'Renamed', the calling function must assign
    the returned name to the original object in the Program or find a
    new fitting name and assign it to the duplicated object using the
    :func:`renameObject` function with the returned string as name.

    .. seealso:: :func:`renameObject` :func:`getFreeName`

    """
    infos_str = json.dumps(dup_infos)
    msg = "DuplicateObjects " + infos_str

    result = connection.send_message(msg)
    results = json.parse(result)

    return results


def undo():
    msg = ("Undo")
    return connection.send_message(msg)


def redo():
    msg = ("Redo")
    return connection.send_message(msg)


def get_free_name(name, max_iters=5000):
    """ Check if the name is in use, if it is, return the next
    unused name by increasing (or adding) the number-suffix

    :param name: the basic name, to check
    :param maxIters: the maximum number of name-checks to perform

    Note: max_iters currently not used in UE4

    :return: string, name that is free

    """
    msg = ("GetFreeName " + name)
    result = connection.send_message(msg)
    return result


def delete_object(name):
    """ Try to delete the object, no return code."""
    msg = ("DeleteObject " + name)
    return connection.send_message(msg)


def parent_child_to(child_name, parent_name):
    """ Set the parent of child_name to be parent_name.

    If parentName is an empty string or None, will parent to the world.

    """
    # TODO: parenting functionality by user choice here or in program?
    if not core.editor.supports_parenting():
        return
    msg = ("ParentChildTo " + child_name)
    if (parent_name is not None) and (parent_name != ''):
        msg = msg + " " + parent_name

    return connection.send_message(msg)


def add_actor_batch(asset_list):
    """ Add an actor to the level for each entry in the asset_list
    each value in the List has to be an `ObjectInfo` instance.
    """
    msg = 'AddActorBatch'
    for obj_info in asset_list:
        line = object_info_to_string(obj_info)
        msg = msg + "\n" + line
    _lg.debug("Assembled add batch command: " + msg)
    return connection.send_message(msg)


def object_info_to_string(obj_info):
    """ Convert an ObjectInfo object into a one-line string as used by
    our UE4-interpreter.

    """
    t = obj_info.position
    r = obj_info.rotation
    s = obj_info.scale
    t = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    r = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    s = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    asset_path = obj_info.attrs.get('asset_path', '')
    asset_path = internal_asset_path_from_asset_file_path(asset_path)
    text = asset_path + " " + obj_info.name + " " + t + " " + r + " " + s
    return text


def internal_asset_path_from_asset_file_path(asset_file_path):
    path, ext = os.path.splitext(asset_file_path)
    if not path.startswith("/") and len(path) > 0:
        path = "/" + path
    if not path.startswith("/Game") and not path.startswith("/Engine"):
        path = "/Game" + path
    path.replace("//", "/")
    return path
