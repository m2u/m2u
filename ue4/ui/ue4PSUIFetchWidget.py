"""
A UE4 specific PySide based UI Widget for Fast-Fetch functionality.

This Widget will be integrated into the m2uMainWindow by the common UI.

"""

import os

from PySide import QtGui

from m2u.ue4 import assets

thispath = os.path.dirname(os.path.realpath(__file__))
icoFetch = QtGui.QIcon(os.path.join(thispath, "icoFetch.png"))


class ue4PSUIFetchWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(ue4PSUIFetchWidget, self).__init__(*args, **kwargs)

        self.buildUI()
        self.connectUI()

    def buildUI(self):
        self.fetchSelectedBtn = QtGui.QPushButton(text="Fast Fetch Selected")
        self.fetchSelectedBtn.setIcon(icoFetch)
        tooltip = ("Get the selected objects from the Editor by exporting to "
                   "a single .fbx file. ")
        self.fetchSelectedBtn.setToolTip(tooltip)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.fetchSelectedBtn)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addStretch()
        self.setLayout(layout)

    def connectUI(self):
        self.fetchSelectedBtn.clicked.connect(self.fetchSelectedBtnClicked)

    def fetchSelectedBtnClicked(self):
        assets.fetch_selected_objects()
