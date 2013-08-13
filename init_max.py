# Called by a macroscript from 3ds Max

# Add the parent directory so python finds our m2u module
import sys, os
baseDir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), ".."
)
sys.path.append(baseDir)

import m2u
reload(m2u)

# Importing them here will make them available for the MaxScript Callbacks
from m2u.max import viewWatcher
# reload(viewWatcher) # for testing
from m2u.max import objectWatcher
# reload(objectWatcher) # for testing

def startup():
    m2u.core.initialize("max")

    # Create GUI here by loading the UI file and hand it the reference to m2u
    from m2u.max import maxGUI
    reload(maxGUI)
    maxGUI.launchGUI()

startup()
