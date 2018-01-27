from m2u.ue4 import selection
from m2u.ue4 import connection


def test_select_by_names(mocker):
    mocker.patch.object(connection, 'send_message')
    names_list = ['name1', 'name2', 'name3']
    selection.select_by_names(names_list)
    connection.send_message.assert_called_once_with(
        "SelectByNames [name1,name2,name3]")


def test_deselect_all(mocker):
    mocker.patch.object(connection, 'send_message')
    selection.deselect_all()
    connection.send_message.assert_called_once_with("DeselectAll")


def test_deselect_by_names(mocker):
    mocker.patch.object(connection, 'send_message')
    names_list = ['name1', 'name2', 'name3']
    selection.deselect_by_names(names_list)
    connection.send_message.assert_called_once_with(
        "DeselectByNames [name1,name2,name3]")
