# udk module init and interface file

import udkUI
import udkTranslator
import udkCommand

#might simply use from udkCommand import * here but that would make things visible which should not be visible here ;)
from udkCommand import transformObject
from udkCommand import setCamera

def connectToInstance():
    """
    find the instance of the editor and establish the required connections
    """
    udkUI.connectToUEd()

#def setCamera(x,y,z,rx,ry,rz):
#    """
#    set the viewport camera
#    """
#    udkCommand.setCamera(x,y,z,rx,ry,rz)


