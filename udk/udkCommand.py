# this file defines functions for actual commands which interact with UDK
import udkUI

def setCamera(x,y,z,rx,ry,rz):
    command = "BUGITGO %f %f %f %f %f %f" % (x,y,z,rx,ry,rz)   
    udkUI.fireCommand(command)
     
