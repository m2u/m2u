"""
UE4 connection module responsible for maintaining a TCP connection to
the UE4 Editor's m2u-Plugin.
Provides basic connect, disconnect and command-sending functionality.

"""

import sys
import logging
import socket

_lg = logging.getLogger(__name__)


this = sys.modules[__name__]

this._socket = None
BUFFER_SIZE = 1024


def connect(*args):
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
    this._socket.connect((tcp_ip, tcp_port))


def send_message(message):
    if this._socket is None:
        _lg.error("Not connected.")
        return
    this._socket.send(message)
    return _receive_message()


def _receive_message():
    if this._socket is None:
        _lg.error("Not connected")
        return None
    data = this._socket.recv(BUFFER_SIZE)
    # print "client received data:", data
    return data


def disconnect():
    if this._socket is not None:
        _lg.info("Closing connection")
        this._socket.close()
        this._socket = None
