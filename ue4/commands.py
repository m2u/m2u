"""Functions for commands which interact with UE4.

Commands will be issued by sending messages through the TCP port.

"""

import os
import logging

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
    connection.send_message(msg)


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
    connection.send_message(msg)


def delete_selected():
    msg = ("DeleteSelected")
    connection.send_message(msg)


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
    if result == "1":
        _lg.error(("No object with name '%s' exists" % name))
        return (False, None)
    if result == new_name:
        return (True, None)
    else:
        # The object was (probably) renamed! but the editor changed the name...
        _lg.warn("Rename returned a different name than desired "
                 "('%s' instead of '%s')." % (result, new_name))
        return (False, result)


# TODO: implement a batch duplicate function for UE and the appropriate
#   caller in maya
def duplicate_object(name, dup_name, t=None, r=None, s=None):
    """Duplicate an object with optional transformations.

    :param name: name of the object to modify
    :param dup_name: desired name for the duplicate
    :param t: translation float tuple or None if not to change
    :param r: rotation float tuple or None if not to change
    :param s: 3d scale float tuple or None if not to change

    :return: tuple (int,string) the int will be
        - 0 if no problem occured
        - 1 if the original object could not be found
        - 2 if the name for the duplicate is already taken
        - 3 if the name was changed by the editor
        - 4 error, reason unknown
    Return values 2 and 3 are mutually exclusive by implementation.
    If 3 is returned, the string will be the name the Editor assigned
    and None otherwise.

    If the return value is 1 or 2, the calling function should change
    the name(s) and try again.
    If the return value is (3,string) the calling function must assign
    the returned name to the original object in the Program or find a new
    fitting name and assign it to the duplicated object using the
    :func:`renameObject` function with the returned string as name.

    .. seealso:: :func:`renameObject` :func:`getFreeName`

    """
    t = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    r = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    s = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    msg = ("DuplicateObject {name} {dup_name} {t} {r} {s}"
           .format(**locals()))
    result = connection.send_message(msg)
    result_values = result.split()
    return_value = int(result_values[0])
    return_name = None
    if len(result_values) > 1:
        return_name = result_values[1]

    if return_value == 1:
        _lg.error("Duplication failed, original object could not be found.")
    elif return_value == 3:
        _lg.warn("Editor returned a different name than desired "
                 "('%s' instead of '%s')." % (return_name, dup_name))
    return (return_value, return_name)


def undo():
    msg = ("Undo")
    connection.send_message(msg)


def redo():
    msg = ("Redo")
    connection.send_message(msg)


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
    connection.send_message(msg)


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

    connection.send_message(msg)


def add_actor_batch(asset_list):
    """ Add an actor to the level for each entry in the asset_list
    each value in the List has to be an `ObjectInfo` instance.
    """
    msg = 'AddActorBatch'
    for obj_info in asset_list:
        line = object_info_to_string(obj_info)
        msg = msg + "\n" + line
    _lg.debug("Assembled add batch command: " + msg)
    connection.send_message(msg)


def object_info_to_string(obj_info):
    """ Convert an ObjectInfo object into a one-line string as used by
    our UE4-interpreter.

    """
    t = obj_info.pos
    r = obj_info.rot
    s = obj_info.scale
    t = "" if t is None else ("T=(%f %f %f)" % (t[0], t[1], t[2]))
    r = "" if r is None else ("R=(%f %f %f)" % (r[0], r[1], r[2]))
    s = "" if s is None else ("S=(%f %f %f)" % (s[0], s[1], s[2]))
    asset_path = internal_asset_path_from_asset_file_path(obj_info.asset_path)
    text = asset_path + " " + obj_info.name + " " + t + " " + r + " " + s
    return text


def internal_asset_path_from_asset_file_path(asset_file_path):
    path, ext = os.path.splitext(asset_file_path)
    if not path.startswith("/") and len(path) > 0:
        path = "/" + path
    asset_path = "/Game" + path
    asset_path.replace("//", "/")
    return asset_path
