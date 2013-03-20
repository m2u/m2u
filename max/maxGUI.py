import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL

from blurdev.gui import Dialog
# from PyQt4.QtGui import QDialog

# this can be changed from outside maybe prior to launch?
uiFilepath = r"C:\Users\Christoph\Desktop\Unreal Level Builder\m2u\core\gui.ui"

class M2UGUI(Dialog):
    
    def __init__( self, parent = None ):
        # super(M2UGUI, self).__init__()
        Dialog.__init__( self, parent )
        self.initUIFromFile( uiFilepath )
        
    def initUIFromFile(self, path):      
        uic.loadUi( path, self )
        self._connect()
        self.show()

    def _connect(self):
        # should be found cause we added m2u to sys.path in the beginning
        from core import hub
        self.connect( self.btnViewFOVDefault, SIGNAL( 'clicked()' ), lambda arg = "default" : hub.program.setViewFOV(arg) )
        self.connect( self.btnViewFOV90, SIGNAL( 'clicked()' ), lambda arg = 90 : hub.program.setViewFOV(arg) ) 
        self.connect( self.ckbToggleSync, SIGNAL( 'clicked()' ), lambda arg = self.ckbToggleSync : hub.program.toggleSync(arg) ) 


def launchGUI():
    # app = QtGui.QApplication(sys.argv)
    # dialog = M2UGUI()
    import blurdev
    blurdev.launch( M2UGUI )
    # sys.exit(app.exec_()) # closes REPL, but default from the zedcode example
    # app.exec_() # does not close the REPL when widget is closed, better for developing

if __name__ == "__main__":
    launchGUI()