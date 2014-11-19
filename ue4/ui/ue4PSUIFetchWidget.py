"""
A UE4 specific PySide based UI Widget for Fast-Fetch functionality.

This Widget will be integrated into the m2uMainWindow by the common UI.

"""

import os

import m2u
editor = m2u.core.getEditor()

from PySide import QtCore
from PySide import QtGui

fpath = os.path.abspath(__file__)
fdir = os.path.dirname(fpath)
icoFetch = QtGui.QIcon(fdir+"/icoFetch.png")

class ue4PSUIFetchWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):  
        super(ue4PSUIFetchWidget, self).__init__(*args, **kwargs)
        
        self.buildUI()
        self.connectUI()

    def buildUI(self):
        self.fetchSelectedBtn = QtGui.QPushButton(text = "Fast Fetch Selected")
        self.fetchSelectedBtn.setIcon(icoFetch)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.fetchSelectedBtn)
        layout.setContentsMargins(1,1,1,1)
        layout.addStretch()
        self.setLayout(layout)

    def connectUI(self):
        self.fetchSelectedBtn.clicked.connect(self.fetchSelectedBtnClicked)

    ################################
    # Callbacks
    ################################

    def fetchSelectedBtnClicked(self):
        editor.ue4Export.fetchSelectedObjects()
        