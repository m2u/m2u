""" Commands for Display Layers.

An Object can always only be member of one Layer. This is not a
restriction by UE4, which allows objects to be in multiple layers, but
a restriction of how many other programs work with display layers
(Maya, Unity).

"""

import logging

from . import connection

_lg = logging.getLogger(__name__)


def add_objects_to_layer(layer_name, obj_list, remove_from_others=True):
    """ Add objects in list to that layer, remove them from all other
    layers.
    If the layer does not exist, it will be created.
    """
    names = "[" + (','.join(obj_list)) + "]"
    msg = ("AddObjectsToLayer {layer} {objects} RemoveFromOthers={remove}"
           .format(layer=layer_name, objects=names, remove=remove_from_others))
    return connection.send_message(msg)


# def remove_object_from_layer(obj_name, layer_name):
#     msg = ("RemoveObjectFromLayer {layer} {object}"
#            .format(layer=layer_name, objects=names))
#     return connection.send_message(msg)


def remove_objects_from_all_layers(obj_list):
    names = "[" + (','.join(obj_list)) + "]"
    msg = ("RemoveObjectsFromAllLayers " + names)
    return connection.send_message(msg)


def rename_layer(old_name, new_name):
    msg = ("RenameLayer {0} {1}".format(old_name, new_name))
    return connection.send_message(msg)


# def createLayer(layerName):
#     msg = ("CreateLayer "+layerName)
#     return ue4Conn.sendMessage(msg)


def delete_layer(layer_name):
    msg = ("DeleteLayer " + layer_name)
    return connection.send_message(msg)


def hide_layer(layer_name):
    msg = ("HideLayer " + layer_name)
    return connection.send_message(msg)


def unhide_layer(layer_name):
    msg = ("UnhideLayer " + layer_name)
    return connection.send_message(msg)
