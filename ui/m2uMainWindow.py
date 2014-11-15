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

from . import m2uIcons as icons
from .m2uExportWindow import m2uExportWindow


class m2uMainWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):  
        super(m2uMainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("m2u "+m2u.getVersion()+" ("
                            +program.getName()+","+editor.getName()+")")
        self.setWindowIcon(icons.m2uIcon32)
        self.buildUI()
        self.connectUI()

        self.exportWindow = m2uExportWindow(parent = self)
        #self.show()
    
    def buildUI(self):
        """create the widgets and layouts"""
        # connect row
        self.topRowLayout = QtGui.QHBoxLayout()
        self.connectBtn = QtGui.QPushButton(text = "Connect")
        self.topRowLayout.addWidget(self.connectBtn)
        self.addressEdit = QtGui.QLineEdit()
        self.topRowLayout.addWidget(self.addressEdit)
        self.topRowLayout.addStretch()
        self.settingsBtn = QtGui.QToolButton()
        self.settingsBtn.setIcon(icons.icoSettings)
        self.topRowLayout.addWidget(self.settingsBtn)
        
        # sync options checkboxes
        self.syncOptionsGrp = QtGui.QGroupBox("Sync Whaaat?")
        layout = QtGui.QGridLayout()
        self.syncCameraChkbx = QtGui.QCheckBox("Sync Camera")
        layout.addWidget(self.syncCameraChkbx,0,0)
        self.syncObjectsChkbx = QtGui.QCheckBox("Sync Objects")
        layout.addWidget(self.syncObjectsChkbx,1,0)
        self.syncSelectionChkbx = QtGui.QCheckBox("Sync Selection")
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
        formLayout.addItem(self.topRowLayout)
        formLayout.addWidget(self.syncOptionsGrp)
        formLayout.addWidget(self.sendGrp)
        #formLayout.setSpacing(1)
        formLayout.setContentsMargins(1,1,1,1)
        formLayout.addStretch()
        self.setLayout(formLayout)
        
        
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
        program.sendSelectedToEd()

    def sendSelNewBtnClicked(self):
        self.exportWindow.show()

