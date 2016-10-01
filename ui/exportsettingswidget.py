
from PySide import QtGui
from PySide import QtCore

from m2u import settings


class PopoverWidget(QtGui.QWidget):
    """A widget that shows as a popup, positioned on the top-right of
    a specified other widget.
    """
    def __init__(self, parent, appendToWidget, *args, **kwargs):
        super(PopoverWidget, self).__init__(parent, *args, **kwargs)
        self.setWindowFlags(QtCore.Qt.Popup)
        self.appendToWidget = appendToWidget

    def show(self):
        point = self.appendToWidget.rect().topRight()
        globalPoint = self.appendToWidget.mapToGlobal(point)
        self.move(globalPoint)
        super(PopoverWidget, self).show()


class ExportSettingsWidget(PopoverWidget):
    def __init__(self, parent, widget, *args, **kwargs):
        super(ExportSettingsWidget, self).__init__(
            parent, widget, *args, **kwargs)

        self.alwaysShowExportWinChkbx = QtGui.QCheckBox(
            "Always show Export Window")
        self.alwaysShowExportWinChkbx.toggled.connect(
            self.alwaysShowExportWinChkbxClicked)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.alwaysShowExportWinChkbx)
        self.setLayout(layout)

        self.loadFromSettings()

    def loadFromSettings(self):
        setting = settings.get_or_default("Export", "bAlwaysShowExportWindow",
                                          'false')
        alwaysShowExportWindow = setting.lower() == "true"
        self.alwaysShowExportWinChkbx.setChecked(alwaysShowExportWindow)

    def alwaysShowExportWinChkbxClicked(self, checked):
        settings.set_option("Export", "bAlwaysShowExportWindow", str(checked))
        settings.save_config()
