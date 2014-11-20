
import m2u

from PySide import QtGui
from PySide import QtCore

settingsSection = "Export"
settingsOption = "bAlwaysShowExportWindow"

class m2uExportSettingsWidget(QtGui.QWidget):
    def __init__(self, parent, widget, *args, **kwargs):  
        super(m2uExportSettingsWidget, self).__init__(parent, *args, **kwargs)
        self.setWindowFlags(QtCore.Qt.Popup)
        self.widget = widget
        
        self.alwaysShowExportWinChkbx = QtGui.QCheckBox("Always show Export Window")
        self.alwaysShowExportWinChkbx.toggled.connect(self.alwaysShowExportWinChkbxClicked)
        self.bAlwaysShowExportWindow = False
        if m2u.settings.config.has_option(settingsSection,settingsOption):
            self.bAlwaysShowExportWindow = m2u.settings.config.getboolean(settingsSection,
                                                                     settingsOption)
        self.alwaysShowExportWinChkbx.setChecked(self.bAlwaysShowExportWindow)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.alwaysShowExportWinChkbx)
        self.setLayout(layout)

    

    def alwaysShowExportWinChkbxClicked(self, checked):
        self.bAlwaysShowExportWindow = checked
        m2u.settings.setOptionCreateSection(settingsSection, settingsOption, 
                                            str(checked))
        m2u.settings.saveConfig()

    def show(self):
        point = self.widget.rect().topRight()
        globalPoint = self.widget.mapToGlobal(point)
        self.move(globalPoint)
        super(m2uExportSettingsWidget, self).show()
        
        