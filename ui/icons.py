"""
icons used by other widgets will be loaded here
"""

import os

from PySide import QtGui

thispath = os.path.dirname(os.path.realpath(__file__))
resFolder = os.path.join(thispath, "res")


icoSettings = QtGui.QIcon(os.path.join(resFolder, "icoSettings.png"))
m2uIcon32 = QtGui.QIcon(os.path.join(resFolder, "m2uIcon32.png"))
m2uIcon128 = QtGui.QIcon(os.path.join(resFolder, "m2uIcon128.png"))

icoSendToEd = QtGui.QIcon(os.path.join(resFolder, "icoSendToEd.png"))
icoExportToEd = QtGui.QIcon(os.path.join(resFolder, "icoExportToEd.png"))

icoTransform = QtGui.QIcon(os.path.join(resFolder, "icoTransform.png"))
icoMesh = QtGui.QIcon(os.path.join(resFolder, "icoMesh.png"))
icoBrowse = QtGui.QIcon(os.path.join(resFolder, "icoBrowse.png"))
icoDoExport = QtGui.QIcon(os.path.join(resFolder, "icoDoExport.png"))
icoDoExportSel = QtGui.QIcon(os.path.join(resFolder, "icoDoExportSel.png"))
icoDoAssign = QtGui.QIcon(os.path.join(resFolder, "icoDoAssign.png"))
icoCancel = QtGui.QIcon(os.path.join(resFolder, "icoCancel.png"))
