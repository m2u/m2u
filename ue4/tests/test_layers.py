from m2u.ue4 import layers
from m2u.ue4 import connection


def test_add_objects_to_layer(mocker):
    mocker.patch.object(connection, 'send_message')
    layer_name = 'layer_1'
    obj_list = ['name1', 'name2', 'name3']
    layers.add_objects_to_layer(layer_name, obj_list, remove_from_others=True)
    connection.send_message.assert_called_once_with(
        "AddObjectsToLayer layer_1 [name1,name2,name3] RemoveFromOthers=True")


def test_remove_objects_from_all_layers(mocker):
    mocker.patch.object(connection, 'send_message')
    obj_list = ['name1', 'name2', 'name3']
    layers.remove_objects_from_all_layers(obj_list)
    connection.send_message.assert_called_once_with(
        "RemoveObjectsFromAllLayers [name1,name2,name3]")


def test_rename_layer(mocker):
    mocker.patch.object(connection, 'send_message')
    layers.rename_layer('old_layer', 'new_layer')
    connection.send_message.assert_called_once_with(
        "RenameLayer old_layer new_layer")


def test_delete_layer(mocker):
    mocker.patch.object(connection, 'send_message')
    layers.delete_layer('layer_1')
    connection.send_message.assert_called_once_with("DeleteLayer layer_1")


def test_hide_layer(mocker):
    mocker.patch.object(connection, 'send_message')
    layers.hide_layer('layer_1')
    connection.send_message.assert_called_once_with("HideLayer layer_1")


def test_unhide_layer(mocker):
    mocker.patch.object(connection, 'send_message')
    layers.unhide_layer('layer_1')
    connection.send_message.assert_called_once_with("UnhideLayer layer_1")
