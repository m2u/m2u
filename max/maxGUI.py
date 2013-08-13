import sys
import m2u

program = m2u.core.getProgram()     

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QApplication # to loop widgets and close existing dialog by name
from PyQt4.QtGui  import QDesktopWidget # to center on screen
from PyQt4.QtCore import Qt, SIGNAL
from blurdev.gui import Dialog
import blurdev

# This can be changed from outside maybe prior to launch?
uiFilepath = r"C:\Users\Christoph\Desktop\Unreal Level Builder\m2u\ui\m2uDialog.ui"
guiInstance = None  # Holds our GUI instance


class M2uGuiDialog(Dialog):

    def __init__(self, parent=None):
        super(M2uGuiDialog, self).__init__()
        self.initUIFromFile(uiFilepath)
        # Protect the memory
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        # Set viewport fov to match the UDK (90 degrees)
        program.setViewFOV("udk")

    def center(self):
        """ Centers GUI on screen """
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def initUIFromFile(self, path):  
        """ Builds GUI using an external .ui file """ 
        uic.loadUi(path, self)
        self.connectSignals()
        self.center()
        self.show()

    def connectSignals(self): 
        """ Connects UI elements to functions """
        # self.connect( self.btnViewFOVDefault, SIGNAL( 'clicked()' ), lambda arg = "default" : hub.program.setViewFOV(arg) )
        # self.connect( self.btnViewFOV90, SIGNAL( 'clicked()' ), lambda arg = "udk" : hub.program.setViewFOV(arg) ) 
        self.connect(self.ckbToggleSyncInteractive, SIGNAL('clicked()'), lambda arg = self.ckbToggleSyncInteractive : program.toggleSync(arg)) 
        self.connect(self.ckbToggleSyncTimebased, SIGNAL('clicked()'), lambda arg = self.ckbToggleSyncTimebased : program.toggleSync(arg)) 
        self.ckbToggleSyncTimebased.clicked[bool].connect(self.toggleSpinner)

    def toggleSpinner(self, checked):
        if checked:
            self.lblInterval.setEnabled(False)
            self.spnInterval.setEnabled(False)
        else:
            self.lblInterval.setEnabled(True)
            self.spnInterval.setEnabled(True)

    def closeEvent(self, evnt):
        """ Makes sure callback/timer is removed when GUI is closed """
        print "m2u: Closing dialog"

        from m2u.max import viewWatcher
        viewWatcher.removeCallback()
        viewWatcher.removeTimer()

        from m2u.max import objectWatcher
        objectWatcher.removeCallback()
        objectWatcher.removeChangeHandler()

        program.setViewFOV("default")

        super(Dialog, self).closeEvent(evnt)

def launchGUI():
    # Kill m2u dialog if already existing 
    for w in QApplication.instance().topLevelWidgets():
        if w.__class__.__name__ == "M2uGuiDialog":
            w.close()
    global guiInstance

    # If we use blurdev.launch, the RepeatTimer (Thread) will crash 3ds Max...
    # guiInstance = blurdev.launch(M2uGuiDialog)

    # So use the default way
    guiInstance = M2uGuiDialog()
    guiInstance.show()

if __name__ == "__main__":
    launchGUI()