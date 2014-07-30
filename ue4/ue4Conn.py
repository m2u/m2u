"""
UE4 connection module responsible for maintaining a TCP connection to the UE4 Editor's m2u-Plugin.
Provides basic connect, disconnect and command-sending functionality.

"""

import socket

_s = None # the socket

def connectToUEd(*args):
    if len(args)<2:
        print "no TCP-endpoint specified, using localhost:3939"
        _openConnection()
    else:
        _openConnection(args)

def _openConnection(TCP_IP = '127.0.0.1', TCP_PORT=3939):
    BUFFER_SIZE = 1024
    global _s
    closeConnection() # make sure the address is freed if we have an old connection
    
    _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _s.connect((TCP_IP, TCP_PORT))
    

def sendMessage(MESSAGE):
    if _s is  None:
        print "Not connected"
        return
    _s.send(MESSAGE)
    return _receiveMessage()
    

def _receiveMessage():
    if _s is  None:
        print "Not connected"
        return
    BUFFER_SIZE = 1024
    data = _s.recv(BUFFER_SIZE)
    #print "client received data:", data
    return data

def closeConnection():
    global _s
    if _s is not None:
        print "Closing connection"
        _s.close()
        _s = None