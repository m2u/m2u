"""Tests that target the real ue4 plugin endpoints.

Under predefined conditions, the return values given from the ue4
plugin implementation must match a specific expected return schema
and/or values.

The main purpose of these tests is to detect changes in how the plugin
implementation interpretes or returns values.

"""

import pytest

from m2u.ue4 import commands


@pytest.mark.ue4
def test_transform_object(with_test_scene):
    result = commands.transform_object(
        'cube_1', t=(1, 2, 3), r=(4, 5, 6), s=(7, 8, 9))
    assert result == 'Ok'


@pytest.mark.ue4
def test_transform_camera(with_test_scene):
    result = commands.transform_camera(1, 2, 3, 4, 5, 6)
    assert result == 'Ok'


@pytest.mark.ue4
def test_delete_selected(with_test_scene):
    result = commands.delete_selected()
    assert result == 'Ok'


@pytest.mark.ue4
def test_rename_object(with_test_scene):
    result = commands.rename_object('cube_1', 'cube_new_name')
    assert result == (True, None)


@pytest.mark.ue4
def test_rename_object_not_found(with_test_scene):
    result = commands.rename_object('cube_not_here', 'cube_new_name')
    assert result == (False, None)


@pytest.mark.ue4
def test_get_free_name(with_test_scene):
    result = commands.get_free_name('cube_1')
    assert result == 'cube_4'


@pytest.mark.ue4
def test_delete_object(with_test_scene):
    result = commands.delete_object('cube_1')
    assert result == 'Ok'


@pytest.mark.ue4
def test_parent_child_to(with_test_scene):
    result = commands.parent_child_to('cube_1', 'sphere_1')
    assert result == 'Ok'


@pytest.mark.xfail
@pytest.mark.ue4
def test_add_actor_batch(mocker):
    asset_list = [
    ]
    raise NotImplementedError()
