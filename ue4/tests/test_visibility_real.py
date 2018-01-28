"""Tests that target the real ue4 plugin endpoints.

Under predefined conditions, the return values given from the ue4
plugin implementation must match a specific expected return schema
and/or values.

The main purpose of these tests is to detect changes in how the plugin
implementation interpretes or returns values.

"""

import pytest

from m2u.ue4 import visibility


@pytest.mark.ue4
def test_hide_selected(with_test_scene):
    result = visibility.hide_selected()
    assert result == 'Ok'


@pytest.mark.ue4
def test_unhide_selected(with_test_scene):
    result = visibility.unhide_selected()
    assert result == 'Ok'


@pytest.mark.ue4
def test_isolate_selected(with_test_scene):
    result = visibility.isolate_selected()
    assert result == 'Ok'


@pytest.mark.ue4
def test_unhide_all(with_test_scene):
    result = visibility.unhide_all()
    assert result == 'Ok'


@pytest.mark.ue4
def test_hide_by_names(with_test_scene):
    result = visibility.hide_by_names(['cube_1', 'cube_2', 'cube_3'])
    assert result == 'Ok'


@pytest.mark.ue4
def test_unhide_by_names(with_test_scene):
    result = visibility.unhide_by_names(['cube_1', 'cube_2', 'cube_3'])
    assert result == 'Ok'
