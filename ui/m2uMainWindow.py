"""
the main window UI

"""
import m2u
program = m2u.core.getProgram()
editor = m2u.core.getEditor()

# we can assume that PySide exists, when this file is loaded
from PySide import QtCore
from PySide import QtGui
#from PySide.QtUiTools import QUiLoader

from . import m2uUI as ui
from . import m2uIcons as icons
from .m2uExportWindow import m2uExportWindow


#class m2uMainWindow(QtGui.QDockWidget):
class m2uMainWindow(ui.windowBaseClass):
    def __init__(self, *args, **kwargs):  
        super(m2uMainWindow, self).__init__(*args, **kwargs)
        
        #self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowFlags(QtCore.Qt.Window)
        #self.setFeatures(self.DockWidgetClosable | self.DockWidgetFloatable)
        #self.setFloating(True)
        self.setWindowTitle("m2u "+m2u.getVersion()+" ("
                            +program.getName()+","+editor.getName()+")")
        self.setWindowIcon(icons.m2uIcon32)
        self.setObjectName("m2uMainWindow")
        self.setStyle(self.parent().style())
        self.buildUI()
        self.connectUI()

        self.exportWindow = m2uExportWindow(parent = self)
    
    def buildUI(self):
        """create the widgets and layouts"""
        # connect row
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(1,1,1,1)
        self.connectBtn = QtGui.QPushButton(text = "Connect")
        layout.addWidget(self.connectBtn)
        self.addressEdit = QtGui.QLineEdit()
        layout.addWidget(self.addressEdit)
        layout.addStretch()
        self.settingsBtn = QtGui.QToolButton()
        self.settingsBtn.setIcon(icons.icoSettings)
        layout.addWidget(self.settingsBtn)
        self.topRowWidget = QtGui.QWidget()
        self.topRowWidget.setLayout(layout)
        
        # sync options checkboxes
        self.syncOptionsGrp = QtGui.QGroupBox("Sync Whaaat?")
        layout = QtGui.QGridLayout()
        self.syncCameraChkbx = QtGui.QCheckBox("Sync Camera")
        layout.addWidget(self.syncCameraChkbx,0,0)
        self.syncObjectsChkbx = QtGui.QCheckBox("Sync Objects")
        layout.addWidget(self.syncObjectsChkbx,1,0)
        self.syncSelectionChkbx = QtGui.QCheckBox("Sync Selection")
        self.syncSelectionChkbx.setDisabled(True)
        layout.addWidget(self.syncSelectionChkbx,1,1)
        self.syncVisibilityChkbx = QtGui.QCheckBox("Sync Visibility")
        layout.addWidget(self.syncVisibilityChkbx,2,0)
        self.syncLayersChkbx = QtGui.QCheckBox("Sync Layers")
        layout.addWidget(self.syncLayersChkbx,3,0)
        layout.setColumnStretch(2,1)
        self.syncOptionsGrp.setLayout(layout)
        
        # send and export buttons
        self.sendGrp = QtGui.QGroupBox("Send/Export")
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1,1,1,1)
        self.sendSelBtn = QtGui.QToolButton()
        self.sendSelBtn.setIcon(icons.m2uIcon128)
        self.sendSelBtn.setIconSize(QtCore.QSize(64,32))
        layout.addWidget(self.sendSelBtn)
        self.sendSelNewBtn = QtGui.QToolButton()
        self.sendSelNewBtn.setIcon(icons.m2uIcon128)
        self.sendSelNewBtn.setIconSize(QtCore.QSize(64,32))
        layout.addWidget(self.sendSelNewBtn)
        layout.addStretch()
        self.sendOptionsBtn = QtGui.QToolButton()
        self.sendOptionsBtn.setIcon(icons.icoSettings)
        self.sendOptionsBtn.setIconSize(QtCore.QSize(32,32))
        layout.addWidget(self.sendOptionsBtn)
        self.sendGrp.setLayout(layout)
        
        # add all onto the main form
        formLayout = QtGui.QVBoxLayout()
        formLayout.addWidget(self.topRowWidget)
        formLayout.addWidget(self.syncOptionsGrp)
        formLayout.addWidget(self.sendGrp)
        #formLayout.setSpacing(1)
        formLayout.setContentsMargins(1,1,1,1)
        formLayout.addStretch()
        # - a widget for this dock widget (a dock widget cannot have a layout itself)
        self.setLayout(formLayout)
        #base = QtGui.QWidget()
        #base.setLayout(formLayout)
        #self.setWidget(base)
        #self.layout = base.layout # yes, overwrite the function
        
        
    def connectUI(self):
        """connect slots to callbacks"""
        self.connectBtn.clicked.connect( self.connectBtnClicked )
        self.settingsBtn.clicked.connect( self.settingsBtnClicked )
        
        self.syncCameraChkbx.toggled.connect( self.syncCameraChkbxClicked )
        self.syncObjectsChkbx.toggled.connect( self.syncObjectsChkbxClicked )
        self.syncSelectionChkbx.toggled.connect( self.syncSelectionChkbxClicked )
        self.syncVisibilityChkbx.toggled.connect( self.syncVisibilityChkbxClicked )
        self.syncLayersChkbx.toggled.connect( self.syncLayersChkbxClicked )
        
        self.sendSelBtn.clicked.connect( self.sendSelBtnClicked )
        self.sendSelNewBtn.clicked.connect( self.sendSelNewBtnClicked )
    
    
    ################################
    # Callbacks
    ################################
    
    def connectBtnClicked(self):
        #get the address from the edit line and pass it to the connect
        #function. We don't care if the address is valid here.
        addr = self.addressEdit.text()
        editor.connectToInstance(addr)
    
    def settingsBtnClicked(self):
        pass
    
    # ---
    
    def syncCameraChkbxClicked(self, checked):
        program.setCameraSyncing(checked)
    
    def syncObjectsChkbxClicked(self, checked):
        program.setObjectSyncing(checked)
    
    def syncSelectionChkbxClicked(self, checked):
        pass
    
    def syncVisibilityChkbxClicked(self, checked):
        program.setVisibilitySyncing(checked)
    
    def syncLayersChkbxClicked(self, checked):
        program.setLayerSyncing(checked)

    # ---

    def sendSelBtnClicked(self):
        op = program.ExportOperation( bOverwrite = False, bImport = True, 
                                      bAssemble = True)
        assetList,untaggedUniquesDetected,taggedDiscrepancyDetected = op.getExportData()
        if untaggedUniquesDetected or taggedDiscrepancyDetected:
            self.exportWindow.setExportDataAndShow(op)
        else: #TODO: implement bAlwaysShowExportWindow option
            # there is no need to show the window, so export automatically
            op.doExport()

    def sendSelNewBtnClicked(self):
        self.exportWindow.show()
        self.exportWindow.raise_()


# ------------------------------------------------------------------------------
