"""UE4 connection module.

Responsible for maintaining a TCP connection to the UE4 Editor's
m2u-Plugin.  Provides basic connect, disconnect and command-sending
functionality.

"""

import sys
import logging
import socket
import struct
import time

_lg = logging.getLogger(__name__)


this = sys.modules[__name__]

this._socket = None
READ_BODY_TIMEOUT_S = 3.0
SOCKET_TIMEOUT_S = 30.0


def connect(*args):
    """Connect to the specified address.

    The first arg is used as the ip address, the second as the port
    number. The first arg may also be a colon separated string of the
    form 'address:port', the second arg will be ignored then. If None
    is provided as the first arg, a default value will be used.

    """
    use_default = True
    ip = '127.0.0.1'
    port = 3939
    if len(args) == 1:
        # Check if only one arg, if it contains a valid ip:port string,
        # split it. If not, replace ip or port, or use both defaults.
        if args[0] is None:
            use_default = True
        else:
            parts = args[0].split(':')
            ip = parts[0]
            use_default = False
            if len(parts) > 1:
                port = int(parts[1])

    elif len(args) == 2:
        ip = args[0]
        port = int(args[1])
        use_default = False

    if use_default:
        _lg.info("No TCP-endpoint specified, using localhost:3939")
        _open_connection()
    else:
        _open_connection(ip, port)


def _open_connection(tcp_ip='127.0.0.1', tcp_port=3939):
    # Make sure the address is freed if we have an old connection.
    disconnect()

    this._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    this._socket.settimeout(SOCKET_TIMEOUT_S)
    this._socket.connect((tcp_ip, tcp_port))


def send_message(message):
    if this._socket is None:
        _lg.error("Not connected.")
        return
    content_length = len(message)
    # Convert to Big Endian int32 and send as header.
    this._socket.sendall(struct.pack('!I', content_length))
    this._socket.sendall(message)
    return _receive_message()


def _receive_message():
    if this._socket is None:
        _lg.error("Not connected")
        return None

    # Get the content length header (4 bytes)
    content_length = this._socket.recv(4)
    if not content_length:
        _lg.error("Could not retrieve message header.")
        return None

    # Convert from Big Endian int32.  Note: unpack returns a tuple.
    content_length, = struct.unpack('!I', content_length)

    time_read_body_start = time.time()
    # Retrieve data from the stream until we read the proposed length
    # of the message or we time out waiting for data.
    message_buffer = b''
    while content_length:
        chunk = this._socket.recv(content_length)
        if not chunk:
            # If the content_length indicates a bigger message than
            # has actually been sent, we might hang in this loop
            # forever, unless we time out.
            time_read_body_duration = time.time() - time_read_body_start
            if time_read_body_duration > READ_BODY_TIMEOUT_S:
                _lg.error("Failed to retrieve full message. "
                          "Expected %i more bytes.", content_length)
                return None
        else:
            message_buffer += chunk
            content_length -= len(chunk)

    return message_buffer


def disconnect():
    if this._socket is not None:
        _lg.info("Closing connection")
        this._socket.close()
        this._socket = None
