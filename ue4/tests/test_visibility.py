from m2u.ue4 import visibility
from m2u.ue4 import connection


def test_hide_selected(mocker):
    mocker.patch.object(connection, 'send_message')
    visibility.hide_selected()
    connection.send_message.assert_called_once_with("HideSelected")


def test_unhide_selected(mocker):
    mocker.patch.object(connection, 'send_message')
    visibility.unhide_selected()
    connection.send_message.assert_called_once_with("UnhideSelected")


def test_isolate_selected(mocker):
    mocker.patch.object(connection, 'send_message')
    visibility.isolate_selected()
    connection.send_message.assert_called_once_with("IsolateSelected")


def test_unhide_all(mocker):
    mocker.patch.object(connection, 'send_message')
    visibility.unhide_all()
    connection.send_message.assert_called_once_with("UnhideAll")


def test_hide_by_names(mocker):
    mocker.patch.object(connection, 'send_message')
    obj_list = ['name1', 'name2', 'name3']
    visibility.hide_by_names(obj_list)
    connection.send_message.assert_called_once_with("HideByNames name1 name2 name3")


def test_unhide_by_names(mocker):
    mocker.patch.object(connection, 'send_message')
    obj_list = ['name1', 'name2', 'name3']
    visibility.unhide_by_names(obj_list)
    connection.send_message.assert_called_once_with("UnhideByNames name1 name2 name3")
