import struct

import pytest

from m2u.ue4 import connection


def test_send_message_no_connection():
    result = connection.send_message("")
    assert result is None


def test_disconnect(mocker):
    mocker.patch.object(connection, '_socket', create=True)
    close = mocker.patch.object(connection._socket, 'close', create=True)
    connection.disconnect()
    close.assert_called_once()
    assert connection._socket is None


def test_receive_message(monkeypatch, mocker):
    message = 'Test message'
    content_length = len(message)
    content_length_big_endian = struct.pack('!I', content_length)

    class MockSocket():
        def recv(self, num_bytes):
            if num_bytes == 4:
                return content_length_big_endian
            return message

    monkeypatch.setattr(connection, '_socket', MockSocket())

    result = connection._receive_message()
    assert result == message


def test_receive_message_timeout(monkeypatch, mocker):
    """Check that we run in a timeout if the socket can't provide all
    the data specified in the content size.

    """
    message = ''
    content_length_big_endian = struct.pack('!I', 1000)

    class MockSocket():
        def recv(self, num_bytes):
            if num_bytes == 4:
                return content_length_big_endian
            return message

    monkeypatch.setattr(connection, '_socket', MockSocket())

    with pytest.raises(connection.ReadBodyTimeoutError):
        connection._receive_message()
