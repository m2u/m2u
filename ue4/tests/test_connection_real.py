import pytest

from m2u.ue4 import connection


@pytest.mark.ue4
def test_send_message_size(with_connection):
    """Send a big message, larger than the servers buffer size, so it
    has to read multiple chunks.

    """
    message = "TestMessageSize " + ("abcdefg" * 5000)
    result = connection.send_message(message)
    assert result == str(len(message))


@pytest.mark.ue4
def test_send_message_unknown_command(with_connection):
    message = "ThisCommandDoesNotExist"
    result = connection.send_message(message)
    assert result == "Command Not Found"
