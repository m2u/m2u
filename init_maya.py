""" maya startup file

called by a shelf button or so, will initialize the system
to use the maya program modules and create the UI attached to maya
"""

import m2u

m2u.core.initialize("maya", "ue4")

# create UI here, send the initialized m2u module to the ui if necessary (max)
# in maya it should be in the maya namespace ?

#createUI(m2u)

#TODO check if pyQt is installed, if not, use the simple internal maya UI

from m2u.maya import mayaInternalUI
mayaInternalUI.createUI()
