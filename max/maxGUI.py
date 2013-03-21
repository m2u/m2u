import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL
from blurdev.gui import Dialog
# from PyQt4.QtGui import QDialog

# this can be changed from outside maybe prior to launch?
uiFilepath = r"C:\Users\Christoph\Desktop\Unreal Level Builder\m2u\core\gui.ui"

# NEED TO RESET VIEW FOV TO 90 EVERYTIME WE USED AN ORTHOGRAPHIC VIEW CAUSE THAT RESETS IT TO 45

class M2UGUI(Dialog):
    
    def __init__( self, parent = None ):
        # super(M2UGUI, self).__init__()
        Dialog.__init__( self, parent )
        self.initUIFromFile( uiFilepath )
        # set viewport fov to match the UDK (90 degrees)
        import max
        max.setViewFOV(90)
        
    def initUIFromFile(self, path):  
        """ Builds GUI using an external .ui file """    
        uic.loadUi( path, self )
        self._connect()
        self.show()

    def _connect(self): # use "_" to not let this function call itself
        """ Connects UI elements to functions """
        from core import hub
        self.connect( self.btnViewFOVDefault, SIGNAL( 'clicked()' ), lambda arg = "default" : hub.program.setViewFOV(arg) )
        self.connect( self.btnViewFOV90, SIGNAL( 'clicked()' ), lambda arg = 90 : hub.program.setViewFOV(arg) ) 
        self.connect( self.ckbToggleSync, SIGNAL( 'clicked()' ), lambda arg = self.ckbToggleSync : hub.program.toggleSync(arg) ) 

    def closeEvent(self, evnt):
        """ Makes sure callbacks are removed when GUI is closed """
        print "m2u: Closing dialog"
        from max import viewWatcher
        viewWatcher.removeCallback()
        super(M2UGUI, self).closeEvent(evnt)

def launchGUI():
    """ Uses blurdev.launch to create the GUI and parent it to 3ds Max """
    # app = QtGui.QApplication(sys.argv)
    # dialog = M2UGUI()
    import blurdev
    blurdev.launch( M2UGUI )
    # sys.exit(app.exec_()) # closes REPL, but default from the zedcode example
    # app.exec_() # does not close the REPL when widget is closed, better for developing

if __name__ == "__main__":
    launchGUI()