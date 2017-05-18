import pytest

from m2u.ue4 import connection


def test_send_message_size():
    """Send a big message, larger than buffer size, so the server has to
    read multiple chunks.

    """
    message = "TestMessageSize " + ("abcdefg" * 5000)
    connection.connect()
    result = connection.send_message(message)
    assert result == str(len(message))
    connection.disconnect()
