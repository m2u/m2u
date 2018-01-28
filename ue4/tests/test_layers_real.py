"""Tests that target the real ue4 plugin endpoints.

Under predefined conditions, the return values given from the ue4
plugin implementation must match a specific expected return schema
and/or values.

The main purpose of these tests is to detect changes in how the plugin
implementation interpretes or returns values.

"""

import pytest

from m2u.ue4 import layers


@pytest.mark.ue4
def test_add_objects_to_layer(with_test_scene):
    result = layers.add_objects_to_layer('layer_1', ['cube_1', ])
    assert result == 'Ok'


@pytest.mark.ue4
def test_remove_objects_from_all_layers(with_test_scene):
    result = layers.remove_objects_from_all_layers(['cube_1', ])
    assert result == 'Ok'


@pytest.mark.ue4
def test_rename_layer(with_test_scene):
    result = layers.rename_layer('layer_1', 'layer_2')
    assert result == 'Ok'


@pytest.mark.ue4
def test_delete_layer(with_test_scene):
    result = layers.delete_layer('layer_1')
    assert result == 'Ok'


@pytest.mark.ue4
def test_hide_layer(with_test_scene):
    result = layers.hide_layer('layer_1')
    assert result == 'Ok'


@pytest.mark.ue4
def test_unhide_layer(with_test_scene):
    result = layers.unhide_layer('layer_1')
    assert result == 'Ok'
