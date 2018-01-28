"""Tests that target the real ue4 plugin endpoints.

Under predefined conditions, the return values given from the ue4
plugin implementation must match a specific expected return schema
and/or values.

The main purpose of these tests is to detect changes in how the plugin
implementation interpretes or returns values.

"""

import pytest

from m2u.ue4 import selection


@pytest.mark.ue4
def test_select_by_names(with_test_scene):
    names_list = ['cube_1', 'cube_2', 'cube_3']
    result = selection.select_by_names(names_list)
    assert result == 'Ok'


@pytest.mark.ue4
def test_deselect_all(with_test_scene):
    result = selection.deselect_all()
    assert result == 'Ok'


@pytest.mark.ue4
def test_deselect_by_names(with_test_scene):
    names_list = ['cube_1', 'cube_2', 'cube_3']
    result = selection.deselect_by_names(names_list)
    assert result == 'Ok'
