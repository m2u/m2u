"""
the asset-export UI

"""
import m2u
program = m2u.core.getProgram()
editor = m2u.core.getEditor()

from PySide import QtCore
from PySide import QtGui

from . import m2uIcons as icons

class m2uExportWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(m2uExportWindow, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(QtCore.Qt.Popup)
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
        self.assetTree.setHeaderLabels(["Assets / Instances","Subpath"])
        leftLayout.addWidget(self.assetTree)
        # - left buttons
        layout = QtGui.QGridLayout()
        self.selectInstancesBtn = QtGui.QPushButton("Select Instances")
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
        self.subpathAssignBtn = QtGui.QPushButton("Assign")
        subpathLayout.addWidget(self.subpathAssignBtn,1,2)
        grpLayout.addItem(subpathLayout)
        # - - prefix and suffix
        prefixLayout = QtGui.QGridLayout()
        label = QtGui.QLabel("Assign Prefix")
        prefixLayout.addWidget(label,0,0)
        self.prefixEdit = QtGui.QLineEdit()
        prefixLayout.addWidget(self.prefixEdit,0,1)
        self.prefixAssignBtn = QtGui.QPushButton("Assign")
        prefixLayout.addWidget(self.prefixAssignBtn,0,2)
        label = QtGui.QLabel("Assign Suffix")
        prefixLayout.addWidget(label,1,0)
        self.suffixEdit = QtGui.QLineEdit()
        prefixLayout.addWidget(self.suffixEdit,1,1)
        self.suffixAssignBtn = QtGui.QPushButton("Assign")
        prefixLayout.addWidget(self.suffixAssignBtn,1,2)
        grpLayout.addItem(prefixLayout)
        
        editGrp.setLayout(grpLayout)
        rightLayout.addWidget(editGrp)
        
        # - right buttons
        layout = QtGui.QGridLayout()
        layout.setColumnStretch(0,1)
        self.assignAssetDataBtn = QtGui.QPushButton("Assing Asset Data (No Export)")
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
        pass

    ################################
    # Callbacks
    ################################
        