# udk module init and interface file

import udkUI
import udkTranslator
import udkCommand

def alive():
    print("hallo")

def connectToInstance():
    """
    find the instance of the editor and establish the required connections
    """
    udkUI.connectToUEd()

def setCamera(x,y,z,rx,ry,rz):
    """
    set the viewport camera
    """
    udkCommand.setCamera(x,y,z,rx,ry,rz)
