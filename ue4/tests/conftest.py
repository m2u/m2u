import pytest

from m2u import core
from m2u import ue4
from m2u.ue4 import connection


@pytest.fixture()
def with_ue4():
    core.editor = ue4


@pytest.fixture(scope='function')
def with_connection(with_ue4):
    connection.connect()
    yield
    connection.disconnect()


@pytest.fixture(scope='function')
def with_test_scene(with_connection):
    connection.send_message('TestInitializeScene')
