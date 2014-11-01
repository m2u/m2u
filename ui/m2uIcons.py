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