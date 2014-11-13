"""
A maya specific PySide based UI Widget for Camera-Setup functionality.

This Widget will be integrated into the m2uMainWindow by the common UI.

"""

import os

import m2u
program = m2u.core.getProgram()

from PySide import QtCore
from PySide import QtGui

fpath = os.path.abspath(__file__)
fdir = os.path.dirname(fpath)
icoCamera = QtGui.QIcon(fdir+"/icoCamera.png")

class mayaPSUICameraWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):  
        super(mayaPSUICameraWidget, self).__init__(*args, **kwargs)
        
        self.buildUI()
        self.connectUI()

    def buildUI(self):
        self.setupCameraBtn = QtGui.QPushButton(text = "Setup Cameras")
        self.setupCameraBtn.setIcon(icoCamera)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.setupCameraBtn)
        layout.setContentsMargins(1,1,1,1)
        layout.addStretch()
        self.setLayout(layout)

    def connectUI(self):
        self.setupCameraBtn.clicked.connect(self.setupCameraBtnClicked)

    ################################
    # Callbacks
    ################################

    def setupCameraBtnClicked(self):
        program.setupCamera()
        