"""
UE4 connection module responsible for maintaining a TCP connection to the UE4 Editor's m2u-Plugin.
Provides basic connect, disconnect and command-sending functionality.

"""

import socket

_s = None # the socket

def connectToUEd(*args):
    useDefault = True
    ip = '127.0.0.1'
    port = 3939
    if len(args)==1:
        #check if only one arg, if it contains a valid ip:port string, split it
        # if not, replace ip or port, or use both defaults
        if args[0] is None:
            useDefault = True
        else:
            parts = args[0].split(':')
            ip = parts[0]
            useDefault = False
            if len(parts)>1:
                port = int(parts[1])
                
    elif len(args)==2:
        ip = args[0]
        port = int(args[1])
        useDefault = False

    if useDefault:
        print "no TCP-endpoint specified, using localhost:3939"
        _openConnection()
    else:
        _openConnection(ip, port)

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