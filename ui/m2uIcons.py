"""
icons used by other widgets will be loaded here
"""

import m2u

resFolder = m2u.core.getM2uBasePath() + "/ui/res/"

#from PySide import QtCore
from PySide import QtGui

icoSettings = QtGui.QIcon(resFolder+"icoSettings.png")
m2uIcon32 = QtGui.QIcon(resFolder+"m2uIcon32.png")
m2uIcon128 = QtGui.QIcon(resFolder+"m2uIcon128.png")

icoSendToEd = QtGui.QIcon(resFolder+"icoSendToEd.png")
icoExportToEd = QtGui.QIcon(resFolder+"icoExportToEd.png")

icoTransform = QtGui.QIcon(resFolder+"icoTransform.png")
icoMesh = QtGui.QIcon(resFolder+"icoMesh.png")
icoBrowse = QtGui.QIcon(resFolder+"icoBrowse.png")
icoDoExport = QtGui.QIcon(resFolder+"icoDoExport.png")
icoDoExportSel = QtGui.QIcon(resFolder+"icoDoExportSel.png")
icoDoAssign = QtGui.QIcon(resFolder+"icoDoAssign.png")
icoCancel = QtGui.QIcon(resFolder+"icoCancel.png")