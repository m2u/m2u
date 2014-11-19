"""
the asset-export UI

This window will receive data from the export process,
that data can then be edited (change names and paths of assets)
and finally send the edited data back to the export process which will then
continue with the actual export.

"""

import os

import m2u
program = m2u.core.getProgram()
editor = m2u.core.getEditor()

from PySide import QtCore
from PySide import QtGui

from . import m2uUI as ui
from . import m2uIcons as icons
from m2u.helper.assetHelper import AssetListEntry

class m2uExportWindow(ui.windowBaseClass):
    def __init__(self, *args, **kwargs):
        super(m2uExportWindow, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(QtCore.Qt.Window)
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("Export")
        self.setWindowIcon(icons.m2uIcon32)
        self.setStyle(self.parent().style())
        self.buildUI()
        self.connectUI()

        #self.exportData = None

        self.italicFont = QtGui.QFont()
        self.italicFont.setItalic(True)
        self.instanceBrush = QtGui.QBrush(QtCore.Qt.darkGray)
        self.discrepancyBrush = QtGui.QBrush(QtCore.Qt.darkRed)
        self.untaggedBrush = QtGui.QBrush(QtCore.Qt.darkYellow)

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
        self.assetTree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.assetTree.setColumnWidth(0,160)
        #self.assetTree.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Preferred)
        #self.assetTree.setIndentation(2)
        leftLayout.addWidget(self.assetTree)
        # - left buttons
        layout = QtGui.QGridLayout()
        self.selectInstancesBtn = QtGui.QPushButton("Select Instances")
        self.selectInstancesBtn.setDisabled(True)
        layout.addWidget(self.selectInstancesBtn,0,0)
        self.removeBtn = QtGui.QPushButton("Remove")
        self.removeBtn.setDisabled(True)
        layout.addWidget(self.removeBtn,1,0)
        self.makeNewBtn = QtGui.QPushButton("Make New Unique(s)")
        self.makeNewBtn.setDisabled(True)
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
        leftWidget.resize(350,200)
        #leftWidget.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Preferred)
        #rightWidget.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Preferred)
        #splitter.setStretchFactor(0,100)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1,1,1,1)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def connectUI(self):
        """connect slots to callbacks"""
        self.cancelBtn.clicked.connect( self.close )
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

    def setExportOperationAndShow(self, operation):
        """ set the temporary data for editing and show the window
        all follow-up export tasks will be called from within the ui

        """
        self.operation = operation
        self.assetTree.clear()
        self.assetItemList = []
        assetList,untaggedUniquesDetected,taggedDiscrepancyDetected = operation.getExportData()
        for entry in assetList:
            lpath,fext = os.path.splitext(entry.assetPath)
            fpath,fname = os.path.split(lpath)
            assetItem = QtGui.QTreeWidgetItem(self.assetTree)
            assetItem.setText(0,fname)
            assetItem.setText(1,fpath)
            assetItem.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable
                               |QtCore.Qt.ItemIsSelectable)
            #assetItem.setIcon(0,icons.icoMesh)
            self.assetItemList.append(assetItem)
            for objTuple in entry.objList:
                objName = objTuple[0]
                objItem = QtGui.QTreeWidgetItem(assetItem)
                objItem.setText(0,objName)
                objItem.setFont(0,self.italicFont)
                #objItem.setDisabled(True)
                objItem.setForeground(0,self.instanceBrush)
                objItem.setIcon(0,icons.icoTransform)
                objItem.objTuple = objTuple # so we don't have to search that data later
                
        self.show()
        self.raise_()

    # def getExportResult(self):
    #     """ get the result of the dialog
    #     0 = cancelled
    #     1 = export
    #     2 = assign-only
    #     call after the dialog has returned
    #     """
    #     pass

    def _getExportData(self):
        """ reassemble the -possibly edited- export data from the tree-entries
        
        """
        assetList = []
        #for i in range(0,self.assetTree.topLevelItemCount()-1):
        for item in self.assetItemList:
            path = item.text(1)
            if not path.endswith("/") and len(path)>0:
                path = path+"/"
            path = path + item.text(0)
            entry = AssetListEntry(path)
            for i in range(0,item.childCount()-1):
                child = item.child(i)
                entry.append(child.objTuple)
            assetList.append(entry)
        return assetList
                

    # ---
    
    def exportAllBtnClicked(self):
        assetList = self._getExportData()
        self.operation.setEditedData(assetList)
        self.operation.doExport()
        self.close()

    def exportSelectedBtnClicked(self):
        assetList = []
        #for i in range(0,self.assetTree.topLevelItemCount()-1):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            path = item.text(1)
            if not path.endswith("/") and len(path)>0:
                path = path+"/"
            path = path + item.text(0)
            entry = AssetListEntry(path)
            for i in range(0,item.childCount()-1):
                child = item.child(i)
                entry.append(child.objTuple)
            assetList.append(entry)
        self.operation.setEditedData(assetList)
        self.operation.doExport()
        self.close()

    def assignAssetDataBtnClicked(self):
        assetList = self._getExportData()
        self.operation.setEditedData(assetList)
        self.operation.doAssignOnly()
        self.close()

    # ---

    def subpathAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            item.setText(1,self.subpathEdit.text())

    def prefixAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            text = item.text(0)
            prefix = self.prefixEdit.text()
            if text.startswith(prefix):
                continue
            text = prefix + text
            item.setText(0,text)

    def suffixAssignBtnClicked(self):
        for item in self.assetItemList:
            if not item.isSelected():
                continue
            text = item.text(0)
            suffix = self.suffixEdit.text()
            if text.endswith(suffix):
                continue
            if suffix.startswith("_"): 
                #TODO: maybe make user-settings set tuple of valid suffix delimiters?
                index = text.rfind("_")
                if index>-1:
                    text = text[:index]
            text = text + suffix
            item.setText(0,text)

    # ---

    def selectInstancesBtnClicked(self):
        pass

    def removeBtnClicked(self):
        pass

    def makeNewBtnClicked(self):
        pass