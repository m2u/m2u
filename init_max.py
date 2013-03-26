# max startup file, called by a macroscript
# will initialize the system to use the max program modules
# and create the UI attached to max

import sys, os

m2uDir = os.path.dirname(os.path.realpath(__file__)) # this script dir
sys.path.append( m2uDir )
# sys.path.append( r"C:\Python26\Lib\site-packages" ) # to get blurdev stuff

# DEPRECATED
# we need persistent global stuff for our callbacks, so we use a little trick
# from Py3dsMax import mxs
# mxs.execute( "python.run(\"" + m2uDir + "\\max\\" + "viewWatcher.py" + "\")" )

# sys.path.append( m2uDir + "\\max" ) 

# THIS ADDS THEM TO THE GLOBAL SCOPE SO IT CAN BE ACCESSED BY MXS CALLBACKS!
from max import viewWatcher
reload(viewWatcher) # for testing
from max import objectWatcher
reload(objectWatcher) # for testing

from core import hub
reload(hub) # for testing

def startup():
    hub.initialize("max")

# do it
startup()
