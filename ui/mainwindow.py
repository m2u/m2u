
# We can assume that PySide exists, when this file is loaded.
from PySide import QtCore
from PySide import QtGui
# from PySide.QtUiTools import QUiLoader

import m2u
from m2u import core
from m2u import ui
from . import icons
from .exportwindow import ExportWindow
from .exportsettingswidget import ExportSettingsWidget


class MainWindow(ui.window_base_class):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowFlags(QtCore.Qt.Window)

        title = "m2u {v} ({p},{e})".format(v=m2u.__version__,
                                           p=core.program.get_name(),
                                           e=core.editor.get_name())
        self.setWindowTitle(title)
        self.setWindowIcon(icons.m2uIcon32)
        self.setObjectName("m2uMainWindow")

        self.exportWindow = ExportWindow(parent=self)

        self.buildUI()
        self.connectUI()

        self.addressEdit.setText("localhost:3939")

    def buildUI(self):
        """create the widgets and layouts"""
        # connect row
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        self.connectBtn = QtGui.QPushButton(text="Connect")
        layout.addWidget(self.connectBtn)
        self.addressEdit = QtGui.QLineEdit()
        layout.addWidget(self.addressEdit)
        layout.addStretch()
        self.settingsBtn = QtGui.QToolButton()
        self.settingsBtn.setIcon(icons.icoSettings)
        self.settingsBtn.setDisabled(True)
        layout.addWidget(self.settingsBtn)
        self.topRowWidget = QtGui.QWidget()
        self.topRowWidget.setLayout(layout)

        # sync options checkboxes
        self.syncOptionsGrp = QtGui.QGroupBox("Sync Whaaat?")
        layout = QtGui.QGridLayout()
        self.syncCameraChkbx = QtGui.QCheckBox("Sync Camera")
        layout.addWidget(self.syncCameraChkbx, 0, 0)
        self.syncObjectsChkbx = QtGui.QCheckBox("Sync Objects")
        layout.addWidget(self.syncObjectsChkbx, 1, 0)
        self.syncSelectionChkbx = QtGui.QCheckBox("Sync Selection")
        self.syncSelectionChkbx.setDisabled(True)
        layout.addWidget(self.syncSelectionChkbx, 1, 1)
        self.syncVisibilityChkbx = QtGui.QCheckBox("Sync Visibility")
        layout.addWidget(self.syncVisibilityChkbx, 2, 0)
        self.syncLayersChkbx = QtGui.QCheckBox("Sync Layers")
        layout.addWidget(self.syncLayersChkbx, 3, 0)
        layout.setColumnStretch(2, 1)
        self.syncOptionsGrp.setLayout(layout)

        # send and export buttons
        self.sendGrp = QtGui.QGroupBox("Send/Export")
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)
        self.sendSelBtn = QtGui.QToolButton()
        self.sendSelBtn.setIcon(icons.icoSendToEd)
        self.sendSelBtn.setIconSize(QtCore.QSize(64, 32))
        self.sendSelBtn.setToolTip("Send selected objects to Editor, assemble the scene. Export assets if necessary.")  # noqa
        layout.addWidget(self.sendSelBtn)
        self.exportSelBtn = QtGui.QToolButton()
        self.exportSelBtn.setIcon(icons.icoExportToEd)
        self.exportSelBtn.setIconSize(QtCore.QSize(64, 32))
        self.exportSelBtn.setToolTip("Export assets of selected objects to Editor. Do not assemble the scene.")  # noqa
        layout.addWidget(self.exportSelBtn)
        layout.addStretch()
        self.sendOptionsBtn = QtGui.QToolButton()
        self.sendOptionsBtn.setIcon(icons.icoSettings)
        self.sendOptionsBtn.setIconSize(QtCore.QSize(32, 32))
        self.exportSettingsWgt = ExportSettingsWidget(parent=self,
                                                      widget=self.sendOptionsBtn)  # noqa
        self.sendOptionsBtn.clicked.connect(self.exportSettingsWgt.show)
        # self.exportSettingsWgt.setParent(self.sendOptionsBtn)
        layout.addWidget(self.sendOptionsBtn)
        self.sendGrp.setLayout(layout)

        # add all onto the main form
        formLayout = QtGui.QVBoxLayout()
        formLayout.addWidget(self.topRowWidget)
        formLayout.addWidget(self.syncOptionsGrp)
        formLayout.addWidget(self.sendGrp)
        formLayout.setContentsMargins(1, 1, 1, 1)
        formLayout.addStretch()
        # A widget for this dock widget
        # (a dock widget cannot have a layout itself)
        self.setLayout(formLayout)
        # base = QtGui.QWidget()
        # base.setLayout(formLayout)
        # self.setWidget(base)
        # self.layout = base.layout # yes, overwrite the function

    def connectUI(self):
        """Connect slots to callbacks."""
        self.connectBtn.clicked.connect(self.connectBtnClicked)
        self.settingsBtn.clicked.connect(self.settingsBtnClicked)

        self.syncCameraChkbx.toggled.connect(self.syncCameraChkbxClicked)
        self.syncObjectsChkbx.toggled.connect(self.syncObjectsChkbxClicked)
        self.syncSelectionChkbx.toggled.connect(self.syncSelectionChkbxClicked)
        self.syncVisibilityChkbx.toggled.connect(self.syncVisibilityChkbxClicked)  # noqa
        self.syncLayersChkbx.toggled.connect(self.syncLayersChkbxClicked)

        self.sendSelBtn.clicked.connect(self.sendSelBtnClicked)
        self.exportSelBtn.clicked.connect(self.exportSelBtnClicked)


    ################################
    # Callbacks
    ################################

    def connectBtnClicked(self):
        # Get the address from the edit line and pass it to the connect
        # function. We don't care if the address is valid here.
        addr = self.addressEdit.text()
        core.editor.connect(addr)

    def settingsBtnClicked(self):
        pass

    # ---

    def syncCameraChkbxClicked(self, checked):
        core.program.set_camera_syncing(bool(checked))

    def syncObjectsChkbxClicked(self, checked):
        core.program.set_object_syncing(bool(checked))

    def syncSelectionChkbxClicked(self, checked):
        pass

    def syncVisibilityChkbxClicked(self, checked):
        core.program.set_visibility_syncing(bool(checked))

    def syncLayersChkbxClicked(self, checked):
        core.program.set_layer_syncing(bool(checked))

    # ---

    def sendSelBtnClicked(self):
        # TODO: what about do_overwrite, once it is implemented?
        op = core.program.ExportOperation(do_overwrite=False, do_import=True,
                                          do_assemble=True)
        self._doExport(op)

    def _doExport(self, op):
        (assetList,
         untaggedUniquesDetected,
         taggedDiscrepancyDetected) = op.get_export_data()

        needsExportWindow = (untaggedUniquesDetected or
                             taggedDiscrepancyDetected or
                             self.exportSettingsWgt.alwaysShowExportWinChkbx.isChecked())  # noqa
        if needsExportWindow:
            self.exportWindow.setExportOperationAndShow(op)
        else:
            # There is no need to show the window, so export automatically
            op.do_export()

    def exportSelBtnClicked(self):
        # TODO: do_overwrite or not?
        op = core.programExportOperation(do_overwrite=True, do_import=True,
                                         do_assemble=False)
        self._doExport(op)
