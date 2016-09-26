
from PySide import QtGui


class SubfolderBrowseDialog(QtGui.QFileDialog):
    """A dialog for choosing a subfolder of a designated top level folder.

    The user should not be able to select any folder that is not a child
    of the top folder.
    """

    def __init__(self, *args, **kwargs):
        super(SubfolderBrowseDialog, self).__init__(*args, **kwargs)

        self.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        self.setOption(QtGui.QFileDialog.ShowDirsOnly)

        self.topLevelDirectory = None

        self.directoryEntered.connect(self.onDirectoryEntered)

    def onDirectoryEntered(self, directory):
        """Prevent navigating into any directory that is not a child of
        the top level directory.
        """
        if not directory.startswith(self.topDirectory):
            self.setDirectory(self.topDirectory)
