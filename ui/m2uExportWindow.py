"""
the asset-export UI

This window will receive data from the export process,
that data can then be edited (change names and paths of assets)
and finally send the edited data back to the export process which will then
continue with the actual export.

"""

# TODO: i would love to have this dialogue to not be required to be modal
# in the current implementation, the export process is blocked until this dialogue
# returns, which makes it impossible for the user to interact with the viewports
# or so to get response as to which objects in the scene are which in the export 
# window. The export process can only continue if necessary data was returned from
# the dialogue.
# alternatives would be to make the dialogue not modal and implement a while-loop
# with integrated event-loop-processing to make the application not hang while
# waiting for the dialogue to return. The problematic point here is the question of
# where to put the event-loop-processing. This may differ depending on if the
# user Program has native PySide support or not, if the m2u-UI is running in a 
# detached thread or not.
# The other option would be to split the export-process into parts which will
# then be called appropriately from within this UI. ... have to think about that

import m2u
program = m2u.core.getProgram()
editor = m2u.core.getEditor()

from PySide import QtCore
from PySide import QtGui

from . import m2uIcons as icons

class m2uExportWindow(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(m2uExportWindow, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("Export")
        self.setWindowIcon(icons.m2uIcon32)
        self.buildUI()
        self.connectUI()

    def buildUI(self):
        """create the widgets and layouts"""
        # left stuff
        leftLayout = QtGui.QVBoxLayout()
        leftLayout.setContentsMargins(1,1,1,1)
        leftWidget = QtGui.QWidget() # widget required for QSplitter
        # - asset tree
        self.assetTree = QtGui.QTreeWidget()
        self.assetTree.setColumnCount(2)
        self.assetTree.setHeaderLabels(["Assets/Instances","Subpath"])
        leftLayout.addWidget(self.assetTree)
        # - left buttons
        layout = QtGui.QGridLayout()
        self.selectInstancesBtn = QtGui.QPushButton("Select Instances")
        self.selectInstancesBtn.setDisabled(True)
        layout.addWidget(self.selectInstancesBtn,0,0)
        self.removeBtn = QtGui.QPushButton("Remove")
        layout.addWidget(self.removeBtn,1,0)
        self.makeNewBtn = QtGui.QPushButton("Make New Unique(s)")
        layout.addWidget(self.makeNewBtn,1,1)
        
        leftLayout.addItem(layout)
        leftWidget.setLayout(leftLayout)
        
        # right stuff
        rightLayout=QtGui.QVBoxLayout()
        rightLayout.setContentsMargins(1,1,1,1)
        rightWidget = QtGui.QWidget()
        # - editing group box
        editGrp = QtGui.QGroupBox("Edit Selected")
        grpLayout = QtGui.QVBoxLayout()
        grpLayout.setContentsMargins(1,1,1,1)
        # - - asset path edit
        subpathLayout = QtGui.QGridLayout()
        label = QtGui.QLabel("Set Asset Subpath")
        subpathLayout.addWidget(label,0,0)
        self.subpathEdit = QtGui.QLineEdit()
        subpathLayout.addWidget(self.subpathEdit,1,0)
        self.subpathBrowseBtn = QtGui.QToolButton()
        subpathLayout.addWidget(self.subpathBrowseBtn,1,1)
        self.subpathAssignBtn = QtGui.QPushButton("Set")
        subpathLayout.addWidget(self.subpathAssignBtn,1,2)
        grpLayout.addItem(subpathLayout)
        # - - prefix and suffix
        prefixLayout = QtGui.QGridLayout()
        label = QtGui.QLabel("Set Prefix")
        prefixLayout.addWidget(label,0,0)
        self.prefixEdit = QtGui.QLineEdit()
        prefixLayout.addWidget(self.prefixEdit,0,1)
        self.prefixAssignBtn = QtGui.QPushButton("Set")
        prefixLayout.addWidget(self.prefixAssignBtn,0,2)
        label = QtGui.QLabel("Set Suffix")
        prefixLayout.addWidget(label,1,0)
        self.suffixEdit = QtGui.QLineEdit()
        prefixLayout.addWidget(self.suffixEdit,1,1)
        self.suffixAssignBtn = QtGui.QPushButton("Set")
        prefixLayout.addWidget(self.suffixAssignBtn,1,2)
        grpLayout.addItem(prefixLayout)
        
        editGrp.setLayout(grpLayout)
        rightLayout.addWidget(editGrp)
        
        # - right buttons
        layout = QtGui.QGridLayout()
        layout.setColumnStretch(0,1)
        self.assignAssetDataBtn = QtGui.QPushButton("Assign Asset Data (No Export)")
        layout.addWidget(self.assignAssetDataBtn,0,1,1,2)
        self.exportSelectedBtn = QtGui.QPushButton("Export Selected")
        layout.addWidget(self.exportSelectedBtn,1,1,1,2)
        self.cancelBtn = QtGui.QPushButton("Cancel")
        layout.addWidget(self.cancelBtn,2,1)
        self.exportAllBtn = QtGui.QPushButton("Export All")
        layout.addWidget(self.exportAllBtn,2,2)
        
        rightLayout.addStretch()
        rightLayout.addItem(layout)
        rightWidget.setLayout(rightLayout)
           
        # add all onto the form (splitted)
        splitter = QtGui.QSplitter()
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1,1,1,1)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def connectUI(self):
        """connect slots to callbacks"""
        self.cancelBtn.clicked.connect( self.reject )
        self.exportAllBtn.clicked.connect( self.exportAllBtnClicked )
        self.assignAssetDataBtn.clicked.connect( self.assignAssetDataBtnClicked )
        self.exportSelectedBtn.clicked.connect( self.exportSelectedBtnClicked )

        self.subpathAssignBtn.clicked.connect( self.subpathAssignBtnClicked )
        self.prefixAssignBtn.clicked.connect( self.prefixAssignBtnClicked )
        self.suffixAssignBtn.clicked.connect( self.suffixAssignBtnClicked )

        self.selectInstancesBtn.clicked.connect( self.selectInstancesBtnClicked )
        self.removeBtn.clicked.connect( self.removeBtnClicked )
        self.makeNewBtn.clicked.connect( self.makeNewBtnClicked )

    ################################
    # Actions and Callbacks
    ################################

    def setData(self, data):
        """ set the temporary data for editing

        call before showing the dialogue

        """
        pass

    def getResult(self):
        """ get the result of the dialog

        0 = cancelled
        1 = export
        2 = assign-only
        call after the dialog has returned

        """

    def getData(self):
        """ get the - possibly edited - data

        you will only receive valid data if the dialog was not cancelled
        
        """
        pass

    # ---
    
    def exportAllBtnClicked(self):
        self.accept()

    def exportSelectedBtnClicked(self):
        self.accept()

    def assignAssetDataBtnClicked(self):
        self.accept()

    # ---

    def subpathAssignBtnClicked(self):
        pass

    def prefixAssignBtnClicked(self):
        pass

    def suffixAssignBtnClicked(self):
        pass

    # ---

    def selectInstancesBtnClicked(self):
        pass

    def removeBtnClicked(self):
        pass

    def makeNewBtnClicked(self):
        pass