"""
m2u main UI module

this is responsible to create a PySide based common UI.

The UI-load-process is initialized by the Program module when requested to generate
the UI by the general initialize script. (program.ui.createUI())

If there is no PySide available, the Program should spawn an internal fallback-UI
by whichever means available to the Program. This module will then never be loaded.

There may exist Program or Editor specific UI parts which can be integrated from
the specific implementations when this module requests them.

It may be necessary for the Program to do some pre-initialization steps to be allow a
PySide based UI to run alongside. It may also generally be necessary to attach the
m2u-window to the Programs main window.

"""
import m2u
program = m2u.core.getProgram()

# we can assume that PySide exists, when this file is loaded
from PySide import QtCore
from PySide import QtGui
from PySide.QtUiTools import QUiLoader

uiFolder = m2u.core.getM2uBasePath() + "/ui/"

def createUI(parentQtWindow = None):
    m2uMainWindow = Cm2uMainWindow(parent = parentQtWindow)
    #m2uMainWindow.setParent(parentQtWindow)


class Cm2uMainWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):  
        super(Cm2uMainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("m2u "+m2u.getVersion()+" ("+program.getName()+")")
        self.initUI()
    
    def initUI(self):
        loader = QUiLoader()
        
        uiFile = QtCore.QFile(uiFolder+"/m2uWindow.ui")
        uiFile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uiFile, parentWidget=self)
        uiFile.close()
        
        self.ui.connectBtn.clicked.connect( self.connectBtnClicked )
        
        self.ui.syncCameraChkbx.toggled.connect( self.syncCameraChkbxClicked )
        
        self.show()
    
    def connectBtnClicked(self):
        print "clicked a buttn"


    def syncCameraChkbxClicked(self, checked):
        pass