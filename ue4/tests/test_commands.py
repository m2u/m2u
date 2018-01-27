import pytest

from m2u.ue4 import commands
from m2u.ue4 import connection
from m2u import core
import m2u.helper.objects


def test_transform_object(mocker):
    mocker.patch.object(connection, 'send_message')
    commands.transform_object('name',
                              t=(1, 2, 3),
                              r=(4, 5, 6),
                              s=(7, 8, 9))
    connection.send_message.assert_called_once_with(
        "TransformObject name "
        "T=(1.000000 2.000000 3.000000) "
        "R=(4.000000 5.000000 6.000000) "
        "S=(7.000000 8.000000 9.000000)")


def test_transform_camera(mocker):
    mocker.patch.object(connection, 'send_message')
    commands.transform_camera(1, 2, 3, 4, 5, 6)
    connection.send_message.assert_called_once_with(
        "TransformCamera 1 2 3 4 5 6 All")


def test_delete_selected(mocker):
    mocker.patch.object(connection, 'send_message')
    commands.delete_selected()
    connection.send_message.assert_called_once_with(
        "DeleteSelected")


def test_rename_object(mocker):
    mocker.patch.object(connection, 'send_message', return_value='new')
    result = commands.rename_object('old', 'new')
    connection.send_message.assert_called_once_with(
        "RenameObject old new")
    assert result == (True, None)


def test_rename_object_not_found(mocker):
    """Test rename result when object to rename was not found."""
    mocker.patch.object(connection, 'send_message', return_value='NotFound')
    result = commands.rename_object('name', 'new_name')
    assert result == (False, None)


def test_rename_object_changed(mocker):
    """Test rename result when desired name was changed."""
    mocker.patch.object(connection, 'send_message', return_value='new_name_2')
    result = commands.rename_object('name', 'new_name')
    assert result == (False, 'new_name_2')


def test_get_free_name(mocker):
    mocker.patch.object(connection, 'send_message')
    commands.get_free_name('name')
    connection.send_message.assert_called_once_with("GetFreeName name")


def test_delete_object(mocker):
    mocker.patch.object(connection, 'send_message')
    commands.delete_object('name')
    connection.send_message.assert_called_once_with("DeleteObject name")


def test_parent_child_to(mocker):
    mocker.patch.object(connection, 'send_message')
    mocker.patch.object(core, 'editor', create=True)
    mocker.patch.object(core.editor, 'supports_parenting', create=True, return_value=True)
    commands.parent_child_to('child', 'parent')
    connection.send_message.assert_called_once_with("ParentChildTo child parent")


@pytest.mark.xfail
def test_add_actor_batch(mocker):
    asset_list = [
    ]
    raise NotImplementedError()


def test_object_info_to_string():
    obj_info = m2u.helper.objects.ObjectInfo(
        'test_name',
        'tet_type_internal',
        'test_type_common',
        attrs={'test_key': 'test_value'},
    )
    expected = '/Game test_name T=(0 0 0) R=(0 0 0) S=(1 1 1)'
    result = commands.object_info_to_string(obj_info)
    assert result == expected


@pytest.mark.xfail
def test_internal_asset_path_from_asset_file_path():
    # TODO: what is the 'asset file path' supposed to be? It has to be
    # relative to some other path, right?
    asset_file_path = 'C:/Users/Usr/dev/ArtSource/Some/File.fbx'
    raise NotImplementedError()
