""" provide a dialog class for choosing a subfolder of a certain top folder.
the user should not be able to select any folder that is not child of the top folder
"""

import os

import m2u

from PySide import QtCore
from PySide import QtGui


class m2uSubfolderBrowseDialog(QtGui.QFileDialog):
    def __init__(self, *args, **kwargs):
        super(m2uSubfolderBrowseDialog, self).__init__(*args, **kwargs)

        self.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        self.setOption(QtGui.QFileDialog.ShowDirsOnly)
        self.directoryEntered.connect(self.directoryEnteredCB)

    def setTopDirectory(self, directory):
        """ set the highest level accessible directory """
        self.topDirectory = directory

    def directoryEnteredCB(self, directory):
        if not directory.startswith(self.topDirectory):
            self.setDirectory(self.topDirectory)